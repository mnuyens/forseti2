import lcm
import forseti2
import time

class TestPiemosController:

    def __init__(self):
        self.lc = lcm.LCM();

    def handle_command(self, channel, data):
        incMsg = forseti2.piemos_cmd.decode(data)
        print(str(incMsg.time))
        print(str(incMsg.header.seq) + " " + str(incMsg.header.time))
        print(channel + ": auton=" + str(incMsg.auton) +
              " enabled=" + str(incMsg.enabled))

if __name__=='__main__':
    try:
        tpc = TestPiemosController()
        for i in range(4):
            tpc.lc.subscribe("piemos"+str(i)+"/cmd", tpc.handle_command)
        while(True):
            tpc.lc.handle()
    except KeyboardInterrupt:
        raise
