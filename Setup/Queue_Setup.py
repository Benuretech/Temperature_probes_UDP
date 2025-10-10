"""
Module: Setup/Queue_Setup.py

Purpose
-------
Lightweight wrappers around multiprocessing.Queue for two payload kinds:
- dict (JSON-like control/status)
- NumPy arrays (pickled blocks)

Design
------
A named "port" = {"q_Main", "q_Sec"} queue pair.
- Queue_Group_Creator builds ports from {name -> size}
- Queue_Sec_port / Main_Queue_port expose JSON_Q helpers per role

JSON_Q API
----------
send()/receive_*() for dicts
send_NP()/receive_*_NP() for NumPy (pickled)

Notes
-----
For high-rate NumPy, consider multiprocessing.shared_memory + a small seq header
to avoid pickling overhead (zero-copy).
"""



from __future__ import annotations

import queue as _queue
import numpy as np
import pickle
import multiprocessing as mp
from typing import Any, Dict, Mapping


# ── Group/Pair builders ─────────────────────────────────────────────────────────

class Queue_Group_Creator:
    """
    Create a group of named queue pairs for main <-> secondary communication.

    Parameters
    ----------
    port_name_dict : Mapping[str, int]
        name -> max queue size (0 = unlimited)

    Attributes
    ----------
    q_group_dict : dict[str, dict[str, mp.Queue]]
        For each name, {"q_Main": ..., "q_Sec": ...}.
    """

    def __init__(self, port_name_dict: Mapping[str, int]) -> None:
        self.port_name_dict = dict(port_name_dict)
        self.q_group_dict: Dict[str, Dict[str, mp.Queue]] = {}

        for name, size in self.port_name_dict.items():
            q_pair_obj = Queue_Pair_Creator(size)
            self.q_group_dict[name] = q_pair_obj.q_pair


class Queue_Pair_Creator:
    """
    Build one bidirectional port = two queues (main<->secondary).

    Parameters
    ----------
    size : int
        Maxsize for each queue (0 = unlimited).

    Attributes
    ----------
    q_Main : mp.Queue  # messages destined for the main process
    q_Sec  : mp.Queue  # messages destined for the secondary process
    q_pair : dict[str, mp.Queue]
    """

    def __init__(self, size: int) -> None:
        self.size = int(size)
        self.q_Main: mp.Queue = mp.Queue(self.size)
        self.q_Sec: mp.Queue = mp.Queue(self.size)
        self.q_pair: Dict[str, mp.Queue] = {"q_Main": self.q_Main, "q_Sec": self.q_Sec}


# ── Ports (role-aware wrappers) ─────────────────────────────────────────────────

class Queue_Sec_port:
    """
    Secondary-side view of a named port.

    Sends to main via q_Main; receives from main via q_Sec.

    Attributes
    ----------
    Port : JSON_Q
        Helper exposing send/receive for dict and NumPy payloads.
    """

    def __init__(self, q_group_dict: Dict[str, Dict[str, mp.Queue]], name: str) -> None:
        self.name = name
        self.q_group_dict = q_group_dict
        self.Port = JSON_Q(
            q_out=self.q_group_dict[self.name]["q_Main"],
            q_in=self.q_group_dict[self.name]["q_Sec"],
        )


class Main_Queue_port:
    """
    Main-side view of all ports.

    Attributes
    ----------
    Port : dict[str, JSON_Q]
        Map of port name -> JSON_Q helper (main sending to secondary).
    """

    def __init__(self, q_group_dict: Dict[str, Dict[str, mp.Queue]]) -> None:
        self.q_group_dict = q_group_dict
        self.Port: Dict[str, JSON_Q] = {}
        for name, pair in self.q_group_dict.items():
            self.Port[name] = JSON_Q(q_out=pair["q_Sec"], q_in=pair["q_Main"])


# ── Payload helper (dicts + NumPy) ─────────────────────────────────────────────

class JSON_Q:
    """
    Wrap a pair of multiprocessing queues with convenience methods.

    Parameters
    ----------
    q_out : mp.Queue
        Outbound queue (this side -> other side).
    q_in : mp.Queue
        Inbound queue (other side -> this side).

    Attributes
    ----------
    JSON_in : dict
        Last received dict payload.
    JSON_out : dict
        Dict payload to send (caller populates then calls send()).
    NP_in : np.ndarray
        Last received NumPy payload (unpickled).
    """


    def __init__(self, q_out: mp.Queue, q_in: mp.Queue) -> None:
        self.q_in = q_in           # queue for receiving
        self.q_out = q_out         # queue for sending

        self.JSON_in: Dict[str, Any] = {}
        self.JSON_out: Dict[str, Any] = {}
        self.NP_in: np.ndarray = np.empty((2, 50))  # placeholder

    # ── Dict payloads ──────────────────────────────────────────────────────────

    def send(self) -> bool:
        """Non-blocking send of `JSON_out` dict; returns False if queue is full."""
        try:
            self.q_out.put_nowait(self.JSON_out)
        except Exception:
            return False
        else:
            return True

    def isempty(self) -> bool:
        """
        True if inbound queue reports empty.

        Warning
        -------
        `multiprocessing.Queue.empty()` can be unreliable across processes.
        Prefer non-blocking receive methods when possible.
        """
        return self.q_in.empty()

    def receive_last(self) -> bool:
        """
        Drain inbound queue and keep only the last dict payload.

        Returns
        -------
        bool
            True if any new dict was received; False otherwise.
        """
        new_data = False
        last: Dict[str, Any] | None = None

        while True:
            try:
                buff = self.q_in.get_nowait()
            except _queue.Empty:
                break
            else:
                last = buff
                new_data = True

        if new_data and last is not None:
            self.JSON_in = last
        return new_data

    def receive_fifo(self) -> bool:
        """
        Pop one dict payload in FIFO order (non-blocking).

        Returns
        -------
        bool
            True if a dict was received; False if queue was empty.
        """
        try:
            buff = self.q_in.get_nowait()
        except _queue.Empty:
            return False
        else:
            self.JSON_in = buff
            return True

    # ── NumPy payloads (pickled) ───────────────────────────────────────────────

    def send_NP(self, nump_array: np.ndarray) -> bool:
        """
        Non-blocking send of a NumPy array, pickled.

        AI_HINT
        -------
        For very high rates, prefer shared memory to avoid pickle overhead.
        """
        try:
            self.q_out.put_nowait(pickle.dumps(nump_array))
        except Exception:
            return False
        else:
            return True

    def receive_last_NP(self) -> bool:
        """
        Drain inbound queue and keep only the last NumPy payload.

        Returns
        -------
        bool
            True if any new array was received; False otherwise.
        """
        new_data = False
        last_bytes: bytes | None = None

        while True:
            try:
                buff = self.q_in.get_nowait()
            except _queue.Empty:
                break
            else:
                last_bytes = buff
                new_data = True

        if new_data and last_bytes is not None:
            self.NP_in = pickle.loads(last_bytes)
        return new_data

    def receive_fifo_NP(self) -> bool:
        """
        Pop one NumPy payload in FIFO order (non-blocking).

        Returns
        -------
        bool
            True if an array was received; False if queue was empty.
        """
        try:
            buff = self.q_in.get_nowait()
        except _queue.Empty:
            return False
        else:
            self.NP_in = pickle.loads(buff)
            return True
