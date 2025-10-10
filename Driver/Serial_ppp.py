"""
Module: Driver/Serial_ppp.py

Purpose
-------
Pack/unpack MCU frames (PPP-like) with:
- Framing: START=0x0D, END=0x0A
- Escaping: ESC=0x1B; byte b ∈ {0x0A, 0x0D, 0x1B} is encoded as (0x1B, 255-b)
- CRC-8: poly=0x07, init=0x00, xorout=0x00, no reflection
- Payloads: N messages, each = 1B CMD + 4B VAL (little-endian)
- LEN: message count (N), included in CRC

Frame Layout (unescaped)
------------------------
START | [ CMD VAL(4) ] * N | LEN | CRC | END

CRC is computed over the unescaped bytes from the first CMD through LEN inclusive,
then CRC itself is appended and the sequence is escaped for transport.

Public API
----------
ppp_format(bytearray) -> tuple(cmd1, val1, cmd2, val2, ...)
messaging_formating({"CMD":..,"VAL":..}) -> bytearray([CMD,VAL])

Notes
-----
- RX path expects a complete datagram/frame (not a streaming parser).
- TX may or may not call add_frame() depending on the MCU's UDP expectations.
"""

from Setup.CMD_TABLE import CmdTable
import struct
from crc import Calculator, Configuration
import copy
from typing import Dict, List, Tuple, Union

class Serial_ppp:
    """
    Build and parse MCU frames with start/end markers, escape sequences, CRC-8,
    and typed value decoding (int32 or float32 from CmdTable).

    Example
    -------
    >>> p = Serial_ppp()
    >>> pkt = p.send_ppp({"CMD": 103, "VAL": 12.5})  # VSET=103, float32
    """

    def __init__(self):
        """
        Init the command table and the CRC-8 calculator.

        CRC-8 configuration:
        - width=8, poly=0x07, init=0x00, xorout=0x00
        - reverse_input=False, reverse_output=False
        """

        self.t = CmdTable()                 # Lookup for command types ("i"/"f")
        self.debug_stream = 0               # Last raw frame (for diagnostics)

       
        self.config = Configuration(width=8,                    # CRC configuration
                                    polynomial=0x07, 
                                    init_value=0x00, 
                                    final_xor_value=0x00, 
                                    reverse_input=False, 
                                    reverse_output=False
                                    )

        self.calculator = Calculator(self.config, optimized=True)  # CRC calculator

    def frame_check(self, bytes_array: bytearray) -> bool:
        """
        Verify START/END and strip them.

        START = 0x0D (\\r), END = 0x0A (\\n)

        Input  : [START] ... [END]
        Output : ...  (START/END removed)

        Returns
        -------
        bool
            True if markers present and overall size is plausible; False otherwise.
        """

        #########################################################################
        #   Check Start and End Frame Byte (\r,0x0D,13)  and l=minimum length   #
        #########################################################################
        inputsize = len(bytes_array)

        if bytes_array[0] != 13 or bytes_array[-1] != 10 or inputsize < 6:
            if bytes_array[0] != 13:
                print("err: no start byte (0x0D):Hex:", " ".join(f"{byte:02X}" for byte in self.debug_stream))
            elif bytes_array[-1] != 10:
                print("err: no end byte(0x0A):Hex:", " ".join(f"{byte:02X}" for byte in self.debug_stream))
            elif len(bytes_array) < 9:
                print("err: too short:Hex:", " ".join(f"{byte:02X}" for byte in self.debug_stream))
            return False

        # Remove START and END
        bytes_array.pop(0)
        bytes_array.pop(-1)
        return True

    def extract_escape(self, bytes_array: bytearray) -> None:
        """
        Remove escape sequences and restore original bytes.

        Rule
        ----
        If byte b ∈ {0x0A, 0x0D, 0x1B}, it's sent as 0x1B, (255 - b).
        """

        temp_byte: List[int] = []
        i = 0

        while i < len(bytes_array):
            if bytes_array[i] != 27:  # Not an escape byte
                temp_byte.append(bytes_array[i])
            else:
                if i + 1 < len(bytes_array):  # Escape byte detected
                    escaped = 255 - bytes_array[i + 1]
                    temp_byte.append(escaped)
                    i += 1
                else:
                    print("Error: Escape byte at end of stream")
                    break
            i += 1
        bytes_array.clear()
        bytes_array.extend(temp_byte)

    def format_check(self, bytes_array):
        """
        Validate message count vs. byte length after unescaping.

        Layout (post START/END removal & unescaping):
        [ CMD VAL(4) ] * N | LEN | CRC

        expected_length = (N * 5) + 2
        """
        message_qty = bytes_array[-2]  # Extract the number of meesages in the frame
        expected_length = message_qty * 5 + 2  # Calculate the expected length of the message

        if expected_length != len(bytes_array):
            print("Length error:", bytes(bytes_array).hex(" "))
            print("expected_length:", expected_length, " vs received_bytes:", len(bytes_array))
            print("RAW DATA:")
            print("Hex:", " ".join(f"{byte:02X}" for byte in self.debug_stream))
            print("RAW DATA END")
            return False
        return True

    def crc_check(self, bytes_array: bytearray) -> bool:
        """
        Verify CRC-8 over [ CMD VAL(4) ] * N | LEN, then strip LEN & CRC.

        On success
        ----------
        Leaves only [ CMD VAL(4) ] * N in `bytes_array`.
        """


        crc_in = bytes_array.pop()                          # CRC byte
        crc_out = self.calculator.checksum(bytes_array)     # checksum over payload+LEN
        bytes_array.pop()                                   # drop LEN

        if crc_in != crc_out:
            print("CRC ERROR:", bytes(bytes_array).hex(" "), "CRC MCU:", crc_in, " vs CRC CPU:", crc_out)
            print("RAW DATA:")
            print("Hex:", " ".join(f"{byte:02X}" for byte in self.debug_stream))
            print("RAW DATA END")
            return False  # return False if the CRC is incorrect
        return True

    def tuple_format(self, bytes_array: bytearray) -> Tuple[Union[int, float], ...]:
        """
        Unpack [ CMD VAL(4) ] * N into a flat tuple: (cmd1, val1, cmd2, val2, ...)

        Endianness: little ('<'), VAL type comes from CmdTable.get_type(CMD).
        """

        total_bytes = len(bytes_array)  # take the total length of the message
        total_messages = int(total_bytes / 5)  # calculate the total number of messages
        structure = "<"  # Little-endian format

        # Build the structure format
        for x in range(0, total_messages):
            structure += "B" + self.t.get_type(bytes_array[x * 5])  # add the datatype of the message


        return struct.unpack(structure, bytes_array)  # extract the message in a tuple of pair CMD and VAL

    def ppp_format(self, bytes_array: bytearray) -> Tuple[Union[int, float], ...]:
        """
        Parse a full frame into (cmd,val,...) if valid; else return ().

        Pipeline
        --------
        frame_check -> extract_escape -> format_check -> crc_check -> tuple_format
        """

        self.debug_stream = copy.deepcopy(bytes_array)
        if self.frame_check(bytes_array):  # check if the frame is correct
            self.extract_escape(bytes_array)  # extract the exit bytes
            if self.format_check(bytes_array):  # check if the length of the message is correct
                if self.crc_check(bytes_array):  # check if the CRC is correct
                    return self.tuple_format(bytes_array)  # extract the message from the byte array
        return tuple()
    # ── Send path helpers ───────────────────────────────────────────────────────

    def send_ppp(self, JSON_message: Dict[str, Union[int, float, str]]) -> bytearray:
        """
        Build a single-message framed packet from {"CMD": <int|str>, "VAL": <int|float|str>}.

        Returns
        -------
        bytearray
            START + escaped([CMD,VAL,LEN,CRC]) + END
        """

        data = self.messaging_formating(JSON_message)  # [CMD VAL(4)]
        self.add_length(data)                          # + LEN (N=1)
        self.add_crc(data)                             # + CRC over unescaped bytes
        ppp_DATA = self.add_frame(data)                # add START/END + escapes
        return ppp_DATA

    def messaging_formating(self, JSON_message: Dict[str, Union[int, float, str]]) -> bytearray:
        """
        Convert {"CMD": ..., "VAL": ...} to little-endian bytes: <B i|f>.
        """

        block_type = self.t.get_type(JSON_message["CMD"])
        val_raw = int(JSON_message["VAL"]) if block_type == "i" else float(JSON_message["VAL"])
        cmd_raw = int(JSON_message["CMD"])
        structure = "<B" + block_type  # set the endianess of the message


        return bytearray(struct.pack(structure, cmd_raw, val_raw))

    def add_crc(self, data: bytearray) -> None:
        """Append CRC-8 of current data (covers [CMD,VAL,...,LEN])."""
        data.append(self.calculator.checksum(data))

    # This function is used to add the start and end frame byte, the exit byte to the message
    def add_frame(self, data: bytearray) -> bytearray:
        """
        Escape special bytes and add START/END.

        Escaped set = {0x0A, 0x0D, 0x1B}. Encode b as ESC, (255-b).
        """
        framed = bytearray()
        for byte in data:
            if byte in (10, 13, 27):
                framed.append(27)
                framed.append(255 - byte)
            else:
                framed.append(byte)
        framed.insert(0, 13)  # START
        framed.append(10)     # END
        return framed

    def add_length(self, data: bytearray) -> None:
        """
        Append LEN = number of messages contained in `data`.

        Note
        ----
        Each message is 5 bytes ([CMD,VAL(4)]), so LEN = len(data) // 5.
        """
        data.append(int(len(data) / 5))
