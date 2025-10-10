"""
Module: Driver/MCU_X86_RJ45.py

Purpose
-------
Process-isolated UDP driver bridging PC <-> MCU.
- Receives PPP frames via Serial_ppp, routes values to inter-process queues
- Sends outbound commands over UDP
- Streams ADC as (3, N) NumPy block: [ts_ns, Va, Ia]
- Maintains link watchdog status (RJ45_ST)

Queues
------
RJ45_CMD : small dict updates (status/telemetry)
RJ45_ADC : NumPy blocks (ADC stream)

Watchdog
--------
- Set RJ45_ST=1 on periodic flush
- Set RJ45_ST=2 if no RX for wd_receive_rate ns
- Optional ping: CMD=250, VAL=8888

ADC Buffer Policy
-----------------
Fill Va and Ia until both reach N. If one channel fills first, keep overwriting
its last slot until the other catches up; then emit the block and reset.
"""

from Setup.Queue_Setup import Queue_Sec_port
from Driver.Serial_ppp import Serial_ppp
from Setup.CMD_TABLE import CmdTable
import time
import socket
from Setup.Time_Cycle import Timer_Cycle
import numpy as np
from typing import Dict, Tuple, Union


class RJ45_UDP:
    """
    UDP communication driver for MCU frames (intended to run in its own process).

    Sockets
    -------
    UDP/IPv4 with 100 ms recv timeout. Bound on host port, sends to `MCU_IP:MCU_PORT`.

    Inter-process
    -------------
    - `self.Port_CMD`: JSON_Q for small dicts to/from GUI/main
    - `self.Port_ADC`: JSON_Q for NumPy blocks (ADC stream)

    Notes
    -----
    - TX framing: current code sends [CMD,VAL,LEN,CRC] without add_frame(); ensure this
      matches the MCU's UDP expectations. If framing is required, call add_frame().

    """

    def __init__(self, q_group):
        # ── Queues for GUI/process integration ──────────────────────────────────


        self.Port_RJ45_obj = Queue_Sec_port(q_group, "RJ45_UDP")
        self.Port_RJ45 = self.Port_RJ45_obj.Port

        # ── Timing and mappings ─────────────────────────────────────────────────
        self.timer_port_refresh = Timer_Cycle(500)    # GUI flush timer (units per Timer_Cycle impl)
        self.t = CmdTable()                           # Command/type lookup
        self.serial_ppp = Serial_ppp()                # PPP parser/packer



        self.HOST_PORT = 8888


        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.1)
        self.sock.bind(("", self.HOST_PORT))


    # ── Receive path ────────────────────────────────────────────────────────────
    def read_ppp(self) -> None:
        """
        Try to read one datagram, parse PPP frames, route values, and perform link checks.

        RX flow
        -------
        recv -> Serial_ppp.ppp_format(bytearray) -> (cmd,val,...) -> collectQT()

        Link checks
        -----------
        - If time since last send > wd_send_rate: send_wd()
        - If time since last receive > wd_receive_rate: set RJ45_ST=2 and push status
        """
        try:
            self.InputRead_Bytes = bytearray(self.sock.recv(1024))
            # For raw debugging, uncomment:
            # print("Hex:", ' '.join(f'{byte:02X}' for byte in self.InputRead_Bytes))
        except Exception:
            # Timeout or no data -> quiet; driver stays responsive.
            pass
        else:
            messages_tuple = self.serial_ppp.ppp_format(self.InputRead_Bytes)
            if messages_tuple:
                # Walk (cmd,val) pairs
                for x2 in range(0, int(len(messages_tuple) / 2)):
                    self.CMD_in = self.t.convert(messages_tuple[x2 * 2])  # mnemonic str
                    self.VAL_in = messages_tuple[x2 * 2 + 1]

                    self.Port_RJ45.JSON_out = {self.CMD_in: [time.perf_counter_ns(), self.VAL_in]}
                    self.Port_RJ45.send()



