import argparse
import lcm
import forseti2
import time
import settings

class TestPiemosController:

    def __init__(self):
        self.lc = lcm.LCM(settings.LCM_URI);

    def handle_command(self, channel, data):
        incMsg = forseti2.piemos_cmd.decode(data)
        print(str(incMsg.game_time))
        print(str(incMsg.header.seq) + " " + str(incMsg.header.time))
        print(channel + ": auton=" + str(incMsg.auton) +
              " enabled=" + str(incMsg.enabled) + " time=" + str(incMsg.game_time))
    def handle_config(self, channel, data):
        print(channel)
        incMsg = forseti2.ConfigData.decode(data)
        print(incMsg.ConfigFile)

    def handle_match(self, channel, data):
        print(channel)
        incMsg = forseti2.match_data.decode(data)
        print(incMsg.TeamName)
        print(incMsg.IsBlueAlliance)
        print(incMsg.FieldObjects)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='test lcm messages to piemos')
    parser.add_argument('-c','--cmd', help='print piemos_cmd\'s', action='store_true')
    parser.add_argument('-C','--Config', help='print ConfigData\'s', action='store_true')
    parser.add_argument('-m','--match', help='print match_data\'s', action='store_true')
    args = parser.parse_args()
    try:
        tpc = TestPiemosController()
        for i in range(4):
            if (args.cmd):
                tpc.lc.subscribe("piemos"+str(i)+"/cmd", tpc.handle_command)
            if (args.Config):
                tpc.lc.subscribe("PiEMOS"+str(i)+"/Config", tpc.handle_config)
            if (args.match):
                tpc.lc.subscribe("piemos"+str(i)+"/match", tpc.handle_match)
        while(True):
            tpc.lc.handle()
    except KeyboardInterrupt:
        raise
