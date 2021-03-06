# Please do not change this hardware control module for Quisk.
# It provides USB control of RS-HFIQ hardware.

from __future__ import print_function

import struct, threading, time, traceback, math
from quisk_hardware_model import Hardware as BaseHardware
import quisk as QS

import serial

DEBUG = 0

serialport = serial.Serial()

class Hardware(BaseHardware):
    def __init__(self, app, conf):
        BaseHardware.__init__(self, app, conf)

        # Default port settings for RS-HFIQ
        serialport.port = "/dev/ttyUSB0"
        serialport.baudrate = 57600
        serialport.bytesize = serial.EIGHTBITS #number of bits per bytes
        serialport.parity = serial.PARITY_NONE #set parity check: no parity
        serialport.stopbits = serial.STOPBITS_ONE #number of stop bits
        serialport.timeout = 1            #non-block read

        try:
            serialport.open()
        except Exception, e:
            print(e)
            raise Exception

        if serialport.isOpen():

            serialport.flushInput() #flush input buffer, discarding all its contents
            serialport.flushOutput()#flush output buffer, aborting current output
            #and discard all that is in buffer

            # Send init string
            print("Sending init string")
            serialport.write("*OF3\r")

            # Wait a moment for init to finish
            time.sleep(2)

        self.vfo = None

        return None
    def open(self):			# Called once to open the Hardware
        if serialport.isOpen():
            # Get RS-HFIQ version string
            serialport.write("*W\r")
            text = serialport.readline()
            print("Retrieved version: ", text)
        return text
    def close(self):			# Called once to close the Hardware

        if serialport.isOpen():
            serialport.close()

        return "Closed"

    def ReturnFrequency(self):
        if serialport.isOpen():
            serialport.write("*F?\r")
            self.current_freq = serialport.readline()
            if DEBUG == 1:
                print("Frequency:", self.current_freq)

        return None, self.current_freq

    def ChangeFrequency(self, tune, vfo, source='', band='', event=None):
        self.vfo = vfo
        if serialport.isOpen():
            vfo_string = "*F" + str(self.vfo) + "\r"
            if DEBUG == 1:
                print("Tuning to: ", vfo_string)
            print("Tuning to: ", self.vfo)
            serialport.write(vfo_string)

        return tune, self.vfo
    def OnPTT(self, ptt):
        print("Transmitting")