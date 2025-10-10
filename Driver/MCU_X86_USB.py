"""
MCU communication driver for USB serial interface.
Handles PPP protocol messaging over serial ports with automatic device detection and connection management.
Provides USB-based communication between PC and MCU with CRC validation and error handling.
"""

from Driver.Serial_ppp import Serial_ppp
import time
import serial
from serial.tools import list_ports
from crc import Calculator, Configuration


class MCU_X86_USB:
    def __init__(self, q_group):
        self.usb_com = USB_Queue(q_group)
        self.serial_ppp = Serial_ppp()
        self.serial_port = None
        self.connected = False

        self.faillure_timeout = time.perf_counter_ns()
        self.received_msg = None

        self.ser = None
        self.config = Configuration(
            width=8,
            polynomial=0x07,
            init_value=0x00,
            final_xor_value=0x00,
            reverse_input=False,
            reverse_output=False,
        )

        self.calculator = Calculator(self.config, optimized=True)
        self.exit = False

    def read_serial_lock(self):
        self.received_msg = self.serial_port.read(1)

    def read_ppp(self):
        if not self.connected:
            print("connection")
            self.connection()
            time.sleep(3)
        elif not self.serial_port.is_open:
            self.connection()
            time.sleep(3)
        else:
            try:
                #############################
                #       Get Data Frame      #
                #############################
                startbyte = self.serial_port.read_until(b"\r")
            except serial.SerialException as e:
                self.connection()
                ###########################
                # Get the raw stream frame
                ###########################
            else:
                #################
                # Find Start Frame Byte (\r,0x0D,13)
                #################
                if startbyte:
                    if startbyte[-1] == 13:
                        #################
                        # start saving the stream
                        #################
                        self.InputRead_Bytes = bytearray(bytes([13]))  # initiate the stream
                        #################
                        # End saving the stream Byte (\n,0x0A,10) or reset if Start Frame Byte (\r,0x0D,13)
                        #################
                        while self.InputRead_Bytes[-1] != 10:
                            self.InputRead_Bytes.extend(bytearray(self.serial_port.read_until()))
                            if self.InputRead_Bytes[-1] == 13:
                                self.InputRead_Bytes = bytearray(bytes([13]))  # initiate the stream

                        messages_tuple = self.serial_ppp.ppp_format(self.InputRead_Bytes)
                        if messages_tuple:
                            for x2 in range(0, int(len(messages_tuple) / 2)):
                                self.usb_com.QT.JSON_out = {
                                    "CMD": messages_tuple[x2 * 2],
                                    "VAL": messages_tuple[x2 * 2 + 1],
                                }
                                self.usb_com.QT.send()

    def send_ppp(self):
        while self.usb_com.QT.receive_fifo():
            ppp_DATA = self.serial_ppp.send_ppp(self.usb_com.QT.JSON_in)

            if not self.connected:
                print("connection")
                self.connection()
                # time.sleep(3)
            elif not self.serial_port.is_open:
                self.connection()

            ################################################
            #       add the start and ending character     #
            ################################################

            else:
                # ffff=bytes(new_DATA)
                print("send 0d", bytes(ppp_DATA).hex(" "), "0a")
                self.serial_port.write(ppp_DATA)

    def connection(self):
        self.connected = False
        try:
            self.serial_port.close()
        except:
            pass

        try:
            self.ports_list = list_ports.comports()
            for device in self.ports_list:
                print("_______________________________________________")
                print("manufacturer:", device.manufacturer)
                print("name:", device.name)
                print("description:", device.description)
                print("hwid:", device.hwid)
                print("vid:", device.vid)
                print("pid:", device.pid)
                print("serial_number:", device.serial_number)
                print("location:", device.location)
                print("product:", device.product)
                print("interface:", device.interface)
                print("_______________________________________________")
                print(device.manufacturer)
                print(device.vid)

                # if (device.manufacturer=="Silicon Labs" or device.vid==4292) or (device.manufacturer=="Microsoft" and device.vid==11914) or (device.manufacturer=="Microsoft" and device.vid==1155 and device.pid==22336):

                if device.manufacturer == "Microsoft" and device.vid == 11914:
                    self.serial_port = serial.Serial(device.device, 921600, 8, "N", 1, timeout=1)

                    if self.serial_port.is_open:
                        self.connected = True
                        print("connected")
                        break
        except:
            self.connected = False

    def close_com(self):
        self.serial_port.close()
