import struct
import time
import serial
import logging


class ArduinoSerial(serial.Serial):
    logger = logging.getLogger(__name__)

    def __init__(self, port, baudrate=115200, timeout=0.05, arduino=True):
        self.with_arduino = arduino
        if self.with_arduino == True:
            super().__init__(port=port, baudrate=baudrate, timeout=timeout)
            time.sleep(0.3)

    def start_serial(self):
        if self.with_arduino and not self.is_open:
            ArduinoSerial.logger.info("Serial communication has started.")
            self.open()
            time.sleep(0.3)

    def close_serial(self):
        if self.with_arduino:
            ArduinoSerial.logger.info("Serial communication has closed.")
            if self.is_open:
                self.communicate((0, 0, 0))
                self.close()

    def communicate(self, rgb: tuple):
        if self.with_arduino and self.is_open:
            r, g, b = rgb
            self.write(struct.pack(">B", r))
            self.write(struct.pack(">B", g))
            self.write(struct.pack(">B", b))
