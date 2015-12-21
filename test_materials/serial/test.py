#!/usr/bin/env python
import serial
import time
class Chassis():
  # a class to handle the serial communication methods to the arm
  # arm firmware is written in c/c++ with use of arduino libs
  # proof of concept  -- needs reply/acknowledge model

  def __init__(self):
    self.com=serial.Serial(baudrate="115200", port="/dev/ttyUSB0")

  def command(self, cmd):
    self.com.flushInput()
    self.com.flushOutput()
    self.com.write("{0}".format(cmd).encode())
    time.sleep(0.3)
    while self.com.inWaiting():
      print(self.com.readline().decode())
      time.sleep(0.3)

    return