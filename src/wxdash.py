#!/usr/bin/python2.7
"""
wxdash.py
Created on Sat Apr  27 12:00:00 2013

@author: kyle



"""

from __future__ import print_function

import wx
import threading
import lcm
import random
import forseti2
import configurator
import settings

BLUE = (24, 25, 141)
GOLD = (241, 169, 50)
DEFAULT_FIELD_ITEMS = "smallfieldmap.json"
FIELD_ITEMS_FOLDER = "../resources/"

class TeamPanel(wx.Panel):

    def __init__(self, remote, letter, number, name, colour, *args, **kwargs):
        super(TeamPanel, self).__init__(*args, **kwargs)
        self.remote = remote
        self.InitUI(letter, number, name, colour)

    def InitUI(self, letter, number, name, colour=None):
        if colour is not None:
            self.SetBackgroundColour(colour)


        dc = wx.ScreenDC()
        self.num_ctrl = wx.TextCtrl(self, size=(dc.GetCharWidth() * 2, dc.GetCharHeight()))
        self.num_ctrl.AppendText(str(number))
        self.get_button = wx.Button(self, label='Get', size=(dc.GetCharWidth() * 2, dc.GetCharHeight()))
        self.get_button.Bind(wx.EVT_BUTTON, self.do_get_name)
        self.name_ctrl = wx.TextCtrl(self, size=(dc.GetCharWidth() * 16,
            dc.GetCharHeight()))
        self.name_ctrl.AppendText(name)

        name_num_box = wx.BoxSizer(wx.HORIZONTAL)
        name_num_box.Add(wx.StaticText(self, label=letter,
            size=(dc.GetCharWidth() * 0.6, dc.GetCharHeight())))
        name_num_box.Add(self.num_ctrl)
        name_num_box.Add(self.get_button)
        name_num_box.Add(self.name_ctrl)

        #button_box = wx.BoxSizer(wx.HORIZONTAL)
        #button_box.Add(wx.Button(self, label='Reset'))
        #button_box.Add(wx.Button(self, label='Configure'))
        #button_box.Add(wx.Button(self, label='Disable'))

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(name_num_box, flag=wx.CENTER)
        #vbox.Add(button_box, flag=wx.CENTER)

        self.SetSizer(self.vbox)
        self.Show(True)

    def do_get_name(self, event):
        self.name = configurator.get_team_name(self.number)

    @property
    def name(self):
        return self.name_ctrl.GetValue()

    @name.setter
    def name(self, val):
        self.name_ctrl.SetValue(val)

    @property
    def number(self):
        try:
            return int(self.num_ctrl.GetValue())
        except ValueError:
            return 0

    @number.setter
    def number(self, val):
        self.num_ctrl.SetValue(str(val))

class MatchControl(wx.Panel):

    def __init__(self, remote, *args, **kwargs):
        super(MatchControl, self).__init__(*args, **kwargs)
        self.remote = remote
        self.InitUI()

    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        dc = wx.ScreenDC()
        match_number = wx.BoxSizer(wx.HORIZONTAL)
        match_number.Add(wx.StaticText(self, label='Match #'.format(1)))
        self.match_num_ctrl = wx.TextCtrl(self, size=(dc.GetCharWidth() * 2,
            dc.GetCharHeight()))
        match_number.Add(self.match_num_ctrl)
        vbox.Add(match_number, flag=wx.CENTER)

        teamSizer = wx.GridSizer(4, 2)
        self.team_panels = [
            TeamPanel(self.remote, 'A', 0, 'Unknown Team', BLUE, self),
            TeamPanel(self.remote, 'C', 0, 'Unknown Team', GOLD, self),
            TeamPanel(self.remote, 'B', 0, 'Unknown Team', BLUE, self),
            TeamPanel(self.remote, 'D', 0, 'Unknown Team', GOLD, self),
            ]
        teamSizer.AddMany(
                [wx.StaticText(self, label='Blue Team'),
                 wx.StaticText(self, label='Gold Team')] +
                [(panel, 0) for panel in self.team_panels]
		)
        vbox.Add(teamSizer, flag=wx.CENTER)
        time_box = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.init_button = wx.Button(self, label='Init')
        self.init_button.Bind(wx.EVT_BUTTON, self.do_init)
        self.go_button = wx.Button(self, label='GO!')
        self.go_button.Bind(wx.EVT_BUTTON, self.do_go)
        self.pause_button = wx.Button(self, label='Pause')
        self.pause_button.Bind(wx.EVT_BUTTON, self.do_pause)
        self.save_button = wx.Button(self, label='Save')
        self.save_button.Bind(wx.EVT_BUTTON, self.do_save)
        self.submit_button = wx.Button(self, label='Submit finalized score')
        self.submit_button.Bind(wx.EVT_BUTTON, self.do_submit)
        self.time_text = wx.StaticText(self, label='0:00')
        self.stage_text = wx.StaticText(self, label='Unknown')
        self.score_text = wx.StaticText(self, label='Score: unknown')
        self.remote.time_text = self.time_text
        buttons.Add(self.save_button, flag=wx.LEFT)
        buttons.Add(self.init_button)
        buttons.Add(self.go_button)
        buttons.Add(self.pause_button)
        buttons.Add(self.submit_button)
        time_box.Add(self.time_text)
        time_box.Add(self.stage_text)
        time_box.Add(self.score_text)
        buttons.Add(time_box)
        vbox.Add(buttons, flag=wx.CENTER)

        self.SetSizer(vbox)
        self.Show(True)

    def do_go(self, e):
        self.remote.do_go()

    def do_pause(self, e):
        self.remote.do_pause()

    def do_save(self, e):
        self.remote.do_save(self.get_match())

    def do_init(self, e):
        self.remote.do_init(self.get_match())

    def do_submit(self, e):
        self.remote.do_submit(self.get_match())

    def _set_match_panel(self, match, team_idx, panel_idx):
        match.team_numbers[team_idx] = self.team_panels[panel_idx].number
        match.team_names[team_idx] = self.team_panels[panel_idx].name

    def _set_panel_match(self, match, team_idx, panel_idx):
        self.team_panels[panel_idx].number = match.team_numbers[team_idx]
        self.team_panels[panel_idx].name = match.team_names[team_idx]

    def get_match(self):
        match = forseti2.Match()
        self._set_match_panel(match, 0, 0)
        self._set_match_panel(match, 1, 2)
        self._set_match_panel(match, 2, 1)
        self._set_match_panel(match, 3, 3)
        try:
            match.match_number = int(self.match_num_ctrl.GetValue())
        except ValueError:
            match.match_number = random.getrandbits(31)
        return match

    def set_match(self, match):
        self._set_panel_match(match, 0, 0)
        self._set_panel_match(match, 1, 2)
        self._set_panel_match(match, 2, 1)
        self._set_panel_match(match, 3, 3)
        self.match_num_ctrl.SetValue(str(match.match_number))

    def set_time(self, match):
        self.time_text.SetLabel(format_time(match.game_time_so_far))
        self.stage_text.SetLabel(match.stage_name)

    def set_score(self, blue, gold):
        self.score_text.SetLabel("Score: Blue {} | {} Gold".format(blue, gold))


class ScheduleControl(wx.Panel):

    def __init__(self, remote, match_control, *args, **kwargs):
        self.remote = remote
        super(ScheduleControl, self).__init__(*args, **kwargs)
        self.InitUI()
        self.remote.match_list_box = self.match_list
        self.match_control = match_control

    def InitUI(self):
        self.match_list = wx.ListBox(self)
        self.match_list.Bind(wx.EVT_LISTBOX, self.choose_match)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.load_button = wx.Button(self, label='Load All')
        self.load_button.Bind(wx.EVT_BUTTON, self.do_load)
        hbox.Add(self.load_button)
        self.clear_first = wx.CheckBox(self, label='Clear first')
        self.clear_first.SetValue(True)
        hbox.Add(self.clear_first)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.match_list, 1, wx.EXPAND)
        vbox.Add(hbox)

        self.SetSizer(vbox)
        self.Show(True)

    def do_load(self, e):
        self.remote.do_load(self.clear_first.GetValue())

    def choose_match(self, event):
        self.match_control.set_match(event.GetClientData())


class MainWindow(wx.Frame):

    def __init__(self, remote, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.remote = remote
        self.InitUI()

    def InitUI(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        match_control = MatchControl(self.remote, self)
        schedule_control = ScheduleControl(self.remote, match_control, self)
        self.remote.match_control = match_control
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(match_control, 0, wx.ALIGN_CENTER | wx.ALIGN_TOP, 8)
        vbox.Add(schedule_control, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 8)

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)

        self.SetSize((800, 600))
        self.SetSizer(vbox)
        self.SetTitle('forseti2 Dashboard')
        self.Centre()
        self.Show(True)

    def OnQuit(self, e):
        self.Close()

def format_match(match):
    print(match.match_number)
    print(match.team_names)
    print(match.team_numbers)
    return '{}: {} ({}) & {} ({}) vs. {} ({}) & {} ({})'.format(
        match.match_number,
        match.team_names[0], match.team_numbers[0],
        match.team_names[1], match.team_numbers[1],
        match.team_names[2], match.team_numbers[2],
        match.team_names[3], match.team_numbers[3],
        )

class Remote(object):

    def __init__(self):
        self.lc = lcm.LCM(settings.LCM_URI)
        self.lc.subscribe('Schedule/Schedule', self.handle_schedule)
        self.lc.subscribe('Timer/Time', self.handle_time)
        self.lc.subscribe('score/state', self.handle_score)
        self.match_list_box = None
        self.match_control = None
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True

    def start(self):
        self.thread.start()

    def _loop(self):
        while True:
            try:
                self.lc.handle()
            except Exception as ex:
                print('Got exception while handling lcm message', ex)

    def handle_schedule(self, channel, data):
        msg = forseti2.Schedule.decode(data)
        for i in range(msg.num_matches):
            self.match_list_box.Insert(format_match(msg.matches[i]), i,
                    msg.matches[i])

    def handle_time(self, channel, data):
        msg = forseti2.Time.decode(data)
        #wx.CallAfter(self.time_text.SetLabel, format_time(msg.game_time_so_far))
        wx.CallAfter(self.match_control.set_time, msg)

    def handle_score(self, channel, data):
        msg = forseti2.score_state.decode(data)
        wx.CallAfter(self.match_control.set_score, msg.blue_total, msg.gold_total)

    def do_load(self, clear_first):
        if clear_first:
            self.match_list_box.Clear()
        msg = forseti2.ScheduleLoadCommand()
        msg.clear_first = clear_first
        print('Requesting load')
        self.lc.publish('Schedule/Load', msg.encode())

    def do_save(self, match):
        self.lc.publish('Match/Save', match.encode())

    def do_init(self, match):
        self.lc.publish('Match/Init', match.encode())

    def do_submit(self, match):
        self.lc.publish('Match/Submit', match.encode())

    def do_time_ctrl(self, command):
        msg = forseti2.TimeControl()
        msg.command_name = command
        self.lc.publish('Timer/Control', msg.encode())

    def do_go(self):
        self.do_time_ctrl('start')

    def do_pause(self):
        self.do_time_ctrl('pause')

def format_time(seconds):
    return '{:d}:{:02.1f}'.format(int(seconds // 60),
                             seconds % 60)


def main():

    app = wx.App()
    remote = Remote()
    MainWindow(remote, None)
    remote.start()
    remote.do_load(False)
    app.MainLoop()


if __name__ == '__main__':
    main()
