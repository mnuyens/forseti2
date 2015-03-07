import wx
import threading
import time
import lcm
import random
import forseti2
import configurator
import settings

BLUE = (24, 25, 141)
GOLD = (241, 169, 50)
RED = (183, 24, 24)
GREEN = (20, 198, 14)

class Overrider(object):

    def __init__(self):
        self.lc = lcm.LCM(settings.LCM_URI)
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.header = forseti2.header()
        self.header.seq = 0;
        self.header.time = time.time()
        self.msg = forseti2.robot_override()
	self.msg.header = self.header
        self.msg.team = 0
        self.msg.override = True

    def _loop(self):
        while True:
            try:
                self.lc.handle()
            except Exception as ex:
                print('Got exception while handling lcm message', ex)

    def start(self):
        self.thread.start()

    def do_override(self, pos, kill):
        self.msg.team = pos
        self.msg.override = kill
	self.msg.header.time = time.time()
        self.lc.publish("robot/override", self.msg.encode())
	self.msg.header.seq += 1


class OverrideMain(wx.Frame):

    def __init__(self, ovdr, *args, **kwargs):
        super(OverrideMain, self).__init__(*args, **kwargs)
        #self.states = [True, True, True, True]
        self.ovdr = ovdr
        self.InitUI()

    def InitUI(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.station1 = wx.ToggleButton(self, id=1, label='Blue Station 1', pos=(300,300), size=(300,300))
        self.station1.Bind(wx.EVT_TOGGLEBUTTON, self.do_ov0, id=1)
        self.station2 = wx.ToggleButton(self, id=2, label='Blue Station 2', pos=(200,100), size=(300,300))
        self.station2.Bind(wx.EVT_TOGGLEBUTTON, self.do_ov1, id=2)
        self.station3 = wx.ToggleButton(self, id=3, label='Gold Station 1', pos=(100,200), size=(300,300))
        self.station3.Bind(wx.EVT_TOGGLEBUTTON, self.do_ov2, id=3)
        self.station4 = wx.ToggleButton(self, id=4, label='Gold Station 2', pos=(200,200), size=(300,300))
        self.station4.Bind(wx.EVT_TOGGLEBUTTON, self.do_ov3, id=4)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.station1, 1, wx.ALIGN_LEFT| wx.ALL)
        hbox1.Add(self.station3, 1, wx.ALIGN_RIGHT | wx.ALL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.station2, 1, wx.ALIGN_LEFT | wx.ALL)
        hbox2.Add(self.station4, 1, wx.ALIGN_RIGHT | wx.ALL)
        vbox.Add(hbox1, 1, wx.ALIGN_TOP, 8)
        vbox.Add(hbox2, 1, wx.ALIGN_BOTTOM, 8)

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)

        self.SetSize((800, 600))
        self.SetSizer(vbox)
        self.SetTitle('Override Dashboard')
        self.Centre()
        self.Show(True)

    def OnQuit(self, e):
        self.Close()

    """def do_override(self, pos):
        self.states[pos] = not self.states[pos]
        self.ovdr.do_override(pos,self.states[pos])"""

    def do_ov0(self, event):
        self.ovdr.do_override(0,self.station1.GetValue())
        #self.do_override(0)

    def do_ov1(self, event):
        self.ovdr.do_override(1,self.station2.GetValue())
        #self.do_override(1)

    def do_ov2(self, event):
        self.ovdr.do_override(2,self.station3.GetValue())
        #self.do_override(2)

    def do_ov3(self, event):
        self.ovdr.do_override(3,self.station4.GetValue())
        #self.do_override(3)



def main():

    app = wx.App()
    ovdr = Overrider()
    OverrideMain(ovdr, None)
    ovdr.start()
    app.MainLoop()


if __name__ == '__main__':
    main()
