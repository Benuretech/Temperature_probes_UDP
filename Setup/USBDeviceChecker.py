"""
This module provides functionality to check if a picoscope is connected to the pc.
It checks the vendor ID and product ID of the connected USB devices and matches them against the Picoscope used in our setup.
If a Picoscope is connected, it returns True, otherwise it returns False. It also stores the product ID of the connected picoscope for further use.
"""

import usb.core
import usb.backend.libusb1
import os
from Setup.Rooth_Path_Finder import rooth_path_finder

class USBDeviceChecker:
    def __init__(self):
        # Load local libusb DLL if present in the script folder

        root_path = rooth_path_finder()

        dll_path = os.path.abspath(os.path.join(root_path, 'libusb-1.0.dll'))
        self.backend = usb.backend.libusb1.get_backend(find_library=lambda x: dll_path)
        
        self.connected_device_id = None

    def is_device_connected(self):
        try:
            devices = usb.core.find(find_all=True, backend=self.backend)
            for dev in devices:
                if dev.idVendor == 0x0CE9 and dev.idProduct in (0x121B, 0x1009):
                    self.connected_device_id = dev.idProduct
                    return True

        except usb.core.USBError as e:
            print(f"[USBError] {e}")
            
        self.connected_device_id = None
        return False
    


