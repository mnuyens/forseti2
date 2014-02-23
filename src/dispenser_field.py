#!/usr/bin/env python2.7

"""
This node controls the real field elements
"""

import lcm
import forseti2 as fs2
import pygame
import time
import math
import threading
import serial
from maestro_ftdi import get_position, pololu_drive

class DispenserHW:
    def __init__(self, team, ser):
        self.team = team
        self.ser = ser
        self.debug = True

    def _dispenser_cmd_handler(self, channel, data):
        msg = fs2.dispenser_cmd.decode(data)
        if self.debug:
            print("Received message on channel \"%s\"" % channel)
            print("   header.seq   = %s" % str(msg.header.seq))
            print("   header.time   = %s" % str(msg.header.time))
            print("   team   = %s" % str(msg.team))
            print("   state   = %s" % str(msg.state))
        if msg.team == self.team:
            for i in range(4):
                setpoint = 0
                if msg.state[i] is fs2.dispenser_cmd.STATE_HELD:
                    setpoint = 2300
                else:
                    setpoint = 500
                pololu_drive(self.ser, i, setpoint)


if __name__ == '__main__':
    try:
        lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
        serial_gold = serial.Serial("/dev/ttyUSB0", baudrate=250000)
        if (get_position(serial_gold, 6) > 512):
            serial_blue = serial.Serial("/dev/ttyUSB1", baudrate=250000)
        else:
            serial_blue = serial_gold
            serial_gold = serial.Serial("/dev/ttyUSB1", baudrate=250000)
        
        dd_gold = DispenserHW(fs2.dispenser_cmd.TEAM_GOLD,
            serial_gold)
        dd_blue = DispenserHW(fs2.dispenser_cmd.TEAM_BLUE,
            serial_blue)
        sub = lc.subscribe("sprocket/field", dd_gold._dispenser_cmd_handler)
        sub = lc.subscribe("sprocket/field", dd_blue._dispenser_cmd_handler)
        while True:
            lc.handle()

    except KeyboardInterrupt:
        raise
    except :
        raise

