# Driver Directory

## Purpose
This folder contains hardware communication drivers for BlueSoft. These modules enable the main applications to interface with field hardware for data acquisition and control, supporting real-time communication and data logging.

## Main Entry Points
- `MCU_X86_RJ45.py`: Communicates with the MCU (Microcontroller Unit) over an RJ45 (Ethernet) connection. Handles command transmission, data retrieval, and protocol management for networked devices.
- `MCU_X86_USB.py`: Provides similar MCU communication as above, but over a USB interface. Used for direct USB-connected hardware.
- `Serial_ppp.py`: Implements a PPP-style (Point-to-Point Protocol) serial communication layer, including message formatting and CRC/error checking for reliable data transfer.
- `Picoscope_Driver/`: Subfolder containing all PicoScope oscilloscope drivers:
	- `Picoscope_Capture_4224.py`, `Picoscope_Capture_4224A.py`: Modules for capturing and processing data from PicoScope 4224/4224A models.
	- `Picoscope_Stream_4224.py`, `Picoscope_Stream_4224A.py`: Modules for real-time streaming data acquisition from PicoScope devices.
	- `Picoscope.py`: Central interface that coordinates and utilizes the specific PicoScope driver modules above.

## Directory Structure
```
Driver/
├── MCU_X86_RJ45.py
├── MCU_X86_USB.py
├── Serial_ppp.py
└── Picoscope_Driver/
		├── Picoscope_Capture_4224.py
		├── Picoscope_Capture_4224A.py
		├── Picoscope_Stream_4224.py
		├── Picoscope_Stream_4224A.py
		└── Picoscope.py
```

Each file or subfolder provides drivers for a specific hardware interface or data acquisition workflow.