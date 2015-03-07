import lcm
import forseti2
import time
import settings

import time
from pyfirmata import Arduino, util
import pyfirmata
#change based on computer
board = Arduino('COM10')


class RobotController:

    def __init__(self):
        self.lc = lcm.LCM(settings.LCM_URI)
        self.header = forseti2.header()
        self.header.seq = 0
        self.header.time = time.time()
        self.auton = False
        self.game_time = 0;
        self.enable = False
        self.team_override= [True,True,True,True]

    def handle_override(self, channel, data):
        incMsg = forseti2.robot_override.decode(data)
        self.team_override[incMsg.team] = not incMsg.override
        self.send_commands()
        

        
        
    def send_commands(self):
        "update with chris's code"
        """
        robot1_auto_pin = 2
        robot1_enable_pin = 3
        robot1_auto_pin = 4
        robot2_enable_pin = 5
        robot2_auto_pin = 6
        robot3_enable_pin = 7
        robot4_auto_pin = 8
        robot4_enable_pin = 9
        """
        starter_pin = 2
        self.header.seq += 1
        for station in range(3):
            enabled = self.enable and self.team_override[station]
            set_control(starter_pin, starter_pin+1, self.auto, enabled)
            starter_pin += 2
            
            
            
    def set_control(pin1, pin2, auto, enable)
        if enable:
            board.digital[pin1].write(0)
        else:
            board.digital[pin1].write(1)
        if auto:
            board.digital[pin2].write(0)
        else:
            board.digital[pin2].write(1)
        
    def handle_gamemode(self, channel, data):
        incMsg = forseti2.ControlData.decode(data)
        self.auton = incMsg.AutonomousEnabled
        self.enable = incMsg.RobotEnabled
        self.game_time = incMsg.Time
        self.send_commands()

if __name__=='__main__':
    try:
        rc = RobotController()
        rc.lc.subscribe("robot/override", rc.handle_override)
        rc.lc.subscribe("robot/Control", rc.handle_gamemode)
        while(True):
            rc.lc.handle()
    except KeyboardInterrupt:
        raise

