import lcm
import forseti2
import time

class PiemosController:

    def __init__(self):
        self.lc = lcm.LCM()
        self.msg = forseti2.piemos_cmd()
        self.msg.header = forseti2.header()
        self.msg.header.seq = 0
        self.msg.header.time = time.time()
        self.msg.auton = False
        self.msg.time = 0;
        self.enable = False
        self.team_override= [True,True,True,True]

    def handle_override(self, channel, data):
        incMsg = forseti2.piemos_override.decode(data)
        self.team_override[incMsg.team] = incMsg.override
        self.send_commands()

    def send_commands(self):
        self.msg.header.seq += 1
        for station in range(4):
            self.msg.enabled = self.enable & self.team_override[station]
            self.msg.header.time = time.time()
            self.lc.publish("piemos"+str(station)+"/cmd", self.msg.encode())

    def handle_gamemode(self, channel, data):
        incMsg = forseti2.ControlData.decode(data)
        self.msg.auton = incMsg.AutonomousEnabled
        self.enable = incMsg.RobotEnabled
        self.msg.time = incMsg.Time
        self.send_commands()

if __name__=='__main__':
    try:
        pc = PiemosController()
        pc.lc.subscribe("piemos/override", pc.handle_override)
        pc.lc.subscribe("piemos/Control", pc.handle_gamemode)
        while(True):
            pc.lc.handle()
    except KeyboardInterrupt:
        raise

