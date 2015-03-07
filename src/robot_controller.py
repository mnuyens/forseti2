import lcm
import forseti2
import time
import settings

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
        self.header.seq += 1
        self.enabled = self.enable and self.team_override[station]

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

