

#!/usr/bin/env python3
# ota_client.py

import os, socket, struct, zlib, time
from typing import Tuple

class OTA_Upload:
    def __init__(self, ip: str, port: int, bin_path: str):
        self.ip = ip
        self.port = port
        self.connect_timeout = 10.0
        self.ready_timeout = 8.0
        self.ack_timeout = 15.0
        self.chunk_size = 64 * 1024
        self.MAX_TRIES = 4
        self.bin_path = bin_path






        if not os.path.exists(bin_path):
            return False, f"file not found: {bin_path}"
        
        size = os.path.getsize(bin_path)

        if size <= 0:
            return False, "empty file"

        crc  = self.file_crc32(self.bin_path)

        for attempt in range(1, self.MAX_TRIES + 1):
            try:    
                with socket.create_connection((self.ip, self.port), timeout=10) as s:
                    s.settimeout(None)  # block while sending

                    # 1) header: length + CRC32 (both little-endian)
                    s.sendall(struct.pack("<I", size))
                    s.sendall(struct.pack("<I", crc))

                    # 2) payload
                    with open(self.bin_path, "rb") as f:
                        while True:
                            chunk = f.read(64 * 1024)
                            if not chunk: break
                            s.sendall(chunk)

                    # 3) wait for reply
                    s.shutdown(socket.SHUT_WR)
                    s.settimeout(10)
                    resp = s.recv(128).decode(errors="ignore").strip()
                    print("MCU:", resp)

                break                     # success → leave loop

            except Exception as e:
                print(f"attempt {attempt}/{self.MAX_TRIES} failed: {e}")
                if attempt == self.MAX_TRIES:
                    raise                 # re-raise on last attempt
                time.sleep(1)             # small backoff before next try


    def file_crc32(self,path):
        crc = 0
        
        with open(path, "rb") as f:
            while True:
                b = f.read(64 * 1024)
                if not b: break
                crc = zlib.crc32(b, crc)
        return crc & 0xFFFFFFFF
