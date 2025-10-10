# Project Communication & MCU Driver Overview

This project contains modules that handle inter-process communication and MCU (Microcontroller Unit) communication over UDP with a custom PPP-based protocol.

## File Overview

### `Setup/Queue_Setup.py`
Provides queue management utilities for inter-process communication using Python's `multiprocessing` queues.

**Key Components:**
- **Queue_Group_Creator** – Creates a dictionary of named queue pairs for communication between processes.
- **Queue_Pair_Creator** – Encapsulates a pair of queues (main ↔ secondary).
- **Queue_Sec_port** – Wraps the "secondary-to-main" queue in a `JSON_Q` object.
- **Main_Queue_port** – Wraps the "main-to-secondary" queue in `JSON_Q` objects.
- **JSON_Q** – A helper class for sending and receiving Python dictionaries and NumPy arrays through queues, with both FIFO and "latest only" modes.

**Purpose:**  
Standardizes and simplifies passing structured data (JSON) or NumPy arrays between the main process and worker processes.

---

### `Driver/MCU_X86_RJ45.py`
Driver module for MCU communication over Ethernet (RJ45) using UDP sockets and a PPP-based custom protocol.

**Key Responsibilities:**
- Maintain bidirectional communication with an MCU via UDP.
- Parse incoming PPP-framed packets and forward them to the main process.
- Handle outgoing commands and watchdog heartbeats.
- Accumulate ADC (Analog-to-Digital Converter) samples until a batch is ready, then send to main process.
- Monitor connection health with watchdog timers.

**Important Concepts:**
- **PPP Protocol Handling:** Encodes/decodes messages with length, CRC, and framing.
- **Watchdog:** Tracks last send/receive times to detect MCU connection issues.
- **ADC Buffering:** Stores interleaved Voltage (`Va`) and Current (`Ia`) readings in a NumPy array before sending.

**Note on Naming:**  
Some identifiers contain typos (`recieve`, `lenght`) that should be corrected for maintainability.

---

## How These Fit Together

1. `Queue_Setup` defines a standard way to pass data between processes.
2. `MCU_X86_RJ45` runs in its own process, uses the queues from `Queue_Setup` to send parsed MCU data to the main GUI thread, and receive commands back.
3. The main GUI/process reads from these queues, processes data, and displays/logs results.

---

## Suggested Improvements
- Fix typos in variable/method names to improve grepability and AI-assisted coding.
- Consider using **shared memory NumPy arrays** for high-throughput ADC streaming to reduce pickling overhead.
- Add partial-flush logic in ADC buffering to handle cases where one channel stops updating.

---
