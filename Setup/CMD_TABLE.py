"""
Module: Setup/CMD_TABLE.py

Purpose
-------
Single source of truth for MCU command space:
- Map mnemonic <-> numeric command code (1 byte on wire)
- Declare the 4-byte value TYPE per command: "i" (int32) or "f" (float32)

Protocol Notes
--------------
Each message on the wire is 1B CMD + 4B VAL (little-endian). This module does
not pack bytes; callers enforce endianness/signedness when (de)serializing VAL.

Public API
----------
CmdTable.convert(x)  : int<->str mapping (113 ⇄ "VRD"; also accepts "113")
CmdTable.get_type(x) : returns "i" or "f" for the VAL packing
CmdTable.parse_hex(w): splits a packed status word into 2-bit fields

Invariants
----------
- CMD codes are unique
- TYPE ∈ {"i","f"}

Examples
--------
>>> t = CmdTable()
>>> t.convert("VRD"), t.get_type(113)
(113, 'f')
"""

from __future__ import annotations
from typing import Dict, Optional, Union, Literal

class CmdTable:
    """
    Manage command mnemonics, numeric codes, and value types for MCU comms.

    Why
    ----
    Centralizes the command space so Python and MCU stay in sync. Provides
    string<->int conversion and a helper to decode 2-bit status fields.

    Concurrency
    -----------
    Read-only after initialization; safe to share across threads/processes.
    """

    def __init__(self):
        # Invariant: H_state names are symbolic only; actual values (0..3) are 2-bit states.
        # Positions here are *field indices* (0..3), not bit masks.
        self.H_state = {
            "T_OFF": 0,
            "T_ON": 1,
            "T_FAIL": 2,
            "T_BUSY": 3,
        }
        # Map of 2-bit field names to their index positions within a packed status word.
        # Each field consumes 2 bits; effective bit offset = position * 2.
        self.array_hex: Dict[str, int] = {
            "ARD": 0,       # Address status          T_OFF(0) / T_ON(1) / T_FAIL(2) / T_BUSY(3)
            "PRD": 1,       # Power status            T_OFF(0) / T_ON(1) / T_FAIL(2) / T_BUSY(3)
            "RSTATUS": 2,   # Ramp status             T_OFF(0) / T_ON(1) / T_FAIL(2) / T_BUSY(3)
            "LAUNCH": 3,    # Launch status           T_OFF(0) / T_ON(1) / T_FAIL(2) / T_BUSY(3)
            "SSR1": 4,      # Solid State Relay 1     2-bit state
            "SSR2": 5,      # Solid State Relay 2     2-bit state
            "SSR3": 6,      # Solid State Relay 3     2-bit state
            "RS485_ST": 7,  # RS485 status            T_OFF(0) / T_ON(1) / T_FAIL(2) / T_BUSY(3)
            "SSR_ST": 8,    # Aggregated SSR status   T_OFF(0) / T_ON(1) / T_FAIL(2) / T_BUSY(3)
            "CAL_ST": 9,    # Calibration status      T_OFF(0) / T_ON(1) / T_FAIL(2) / T_BUSY(3)
        }

        # Command dictionary:
        # - CMD: numeric command byte (will be truncated to 1 byte when serialized)
        # - TYPE: payload interpretation for the 4-byte value ("i" or "f")
        # AI_HINT: Keep names consistent and stable; callers and docs rely on these mnemonics.
        self.array_table: Dict[str, Dict[str, Union[int, Literal["i", "f"]]]] = {
            "RTD1": {"CMD": 101, "TYPE": "i"},   # Set address
            "RTD2": {"CMD": 102, "TYPE": "i"},   # Power ON/OFF
            "RTD3": {"CMD": 103, "TYPE": "i"},   # Voltage limit
            "RTD4": {"CMD": 104, "TYPE": "i"},   # Current limit
            "FAULT_RTD1": {"CMD": 111, "TYPE": "i"},   # Version
            "FAULT_RTD2":  {"CMD": 112, "TYPE": "i"},   # Read address
            "FAULT_RTD3":  {"CMD": 113, "TYPE": "i"},   # Read power ON/OFF
            "FAULT_RTD4":  {"CMD": 114, "TYPE": "i"},   # Read voltage limit
            "ADC1":  {"CMD": 121, "TYPE": "i"},   # Read current limit
            "ADC2":   {"CMD": 122, "TYPE": "i"},   # Measure Vout
            "ADC3":   {"CMD": 123, "TYPE": "i"},   # Measure Iout
            "ADC4":   {"CMD": 124, "TYPE": "i"},   # Temperature T1

        }

        # Precomputed lookup maps for fast conversion.
        self.t_123_abc: Dict[int, str] = {v["CMD"]: k for k, v in self.array_table.items()}
        self.t_abc_123: Dict[str, int] = {k: v["CMD"] for k, v in self.array_table.items()}

    # ── Public API ───────────────────────────────────────────────────────────────

    def convert(self, x: Union[int, str]) -> Union[str, int, bool]:
        """
        Convert a command identifier between mnemonic and numeric code.

        Parameters
        ----------
        x : int or str
            - int  -> treated as numeric CMD; returns mnemonic (str) or None/False
            - str  -> digits => decimal CMD; otherwise mnemonic name

        Returns
        -------
        str | int | bool
            - str mnemonic when input was a numeric code
            - int numeric code when input was a mnemonic
            - False if no mapping exists (legacy sentinel preserved)

        Notes
        -----
        Input like "113" is supported for convenience.
        """
        try:
            if isinstance(x, int):
                return self.t_123_abc.get(x)
            elif isinstance(x, str) and x.isdigit():
                return self.t_123_abc.get(int(x))
            return self.t_abc_123.get(x)  # may be None
        except KeyError:
            # Defensive: dict.get() doesn't raise KeyError; kept to preserve original intent.
            return False


    def get_type(self, x: Union[int, str]) -> Literal["i", "f"]:
        """
        Get the declared payload type for a command.

        Parameters
        ----------
        x : int or str
            Command numeric code (int), mnemonic (str), or digit string.

        Returns
        -------
        Literal["i","f"]
            "i" for 32-bit integer, "f" for 32-bit float.
            Defaults to "i" if unknown (preserves current behavior).
        """
        try:
            cmd_key = self.convert(x)
            if cmd_key:
                return self.array_table[cmd_key]["TYPE"]  # type: ignore[index]
        except KeyError:
            pass
        return "i"  # Default if not found (legacy behavior)


    def parse_hex(self, status_word: int) -> Dict[str, int]:
        """
        Decode 2-bit fields from a packed status word.

        Parameters
        ----------
        x : int
            Integer whose bits contain multiple 2-bit statuses. Each entry in
            `array_hex` indicates the field position (0-based). The field value is:
            (x >> (position * 2)) & 0b11.

        Returns
        -------
        dict[str, int]
            Field name -> 2-bit code (0..3), used with T_OFF/T_ON/T_FAIL/T_BUSY.
        """
        # Extract (status_word >> (pos * 2)) & 0b11 for each named field.
        return {name: ((status_word >> (pos * 2)) & 0b11) for name, pos in self.array_hex.items()}