#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
timer.py
Created on Wed Apr 24 12:00:00 2013

@author: kyle


"""
from __future__ import print_function

import forseti2
import configurator
import json
import lcm
import threading
import time
import random
import os
import settings
import util
import LCMNode

Node = LCMNode.Node
LCMNode = LCMNode.LCMNode

class Timer(object):

    def __init__(self):
        self.segments = []
        self.segment_start_time = time.time()
        self.running = False

    def _this_segment_time(self):
        return time.time() - self.segment_start_time

    def time(self):
        if self.running:
            return sum(self.segments) + self._this_segment_time()
        else:
            return sum(self.segments)

    def start(self):
        if not self.running:
            self.running = True
            self.segment_start_time = time.time()
        return self

    def pause(self):
        if not self.running:
            return self
        self.running = False
        self.segments.append(self._this_segment_time())
        return self

    def add(self, additional_time):
        self.segments.append(additional_time)

    def subtract(self, less_time):
        self.segments.append(-less_time)

    def reset(self):
        self.__init__()
        return self

class Period(object):

    def __init__(self, name, length, autocontinue=False):
        self.name = name
        self.length = length
        self.autocontinue = autocontinue

class MatchTimer(LCMNode):

    def __init__(self, lc, match):
        self.stage_ended = False
        self.lc = lc
        self.match = match
        self.stages = [Period('Setup', 0),
            Period('Autonomous', settings.AUTONOMOUS_LENGTH_SECONDS, True), Period('Paused', 0),
            Period('Teleop', settings.TELEOP_LENGTH_SECONDS, True), Period('End', 0)]
        self.stage_index = 0
        self.match_timer = Timer()
        self.stage_timer = Timer()
        self.lc.subscribe('Timer/Control', self.handle_control)
        self.lc.subscribe('Match/Init', self.handle_init)
        self.start_thread()
        self.on_stage_change(None, self.stages[0])

    def reset(self):
        self.stage_index = 0
        self.match_timer.reset()
        self.stage_timer.reset()
        self.on_stage_change(self.stages[self.stage_index], self.stages[0])
        self.stage_ended = True

    def current_stage(self):
        return self.stages[self.stage_index]

    def check_for_stage_change(self):
        if self.stage_timer.time() > self.current_stage().length:
            self.stage_timer.reset()
            self.stage_ended = True
            if self.current_stage().autocontinue:
                self.stage_index += 1
                self.on_stage_change(self.stages[self.stage_index - 1],
                    self.stages[self.stage_index])
                self.pause()
            else:
                #print('Stage = ', self.current_stage().name)
                self.pause()

    def on_stage_change(self, old_stage, new_stage):
        if new_stage.name == 'Setup':
            self.match.stage = 'Autonomous'
            self.match.disable_all()
            self.pause()
        elif new_stage.name == 'Autonomous':
            self.match.stage = 'Autonomous'
            self.match.enable_all()
        elif new_stage.name == 'Paused':
            self.match.stage = 'Paused'
            self.match.disable_all()
            self.pause()
        elif new_stage.name == 'Teleop':
            self.match.stage = 'Teleop'
            self.match.enable_all()
        elif new_stage.name == 'End':
            self.match.stage = 'End'
            self.pause()

    def start(self):
        self.match_timer.start()
        self.stage_timer.start()
        if self.stage_ended and self.stage_index + 1 < len(self.stages):
            self.stage_index += 1
            self.stage_ended = False
            self.on_stage_change(self.stages[self.stage_index - 1],
                self.stages[self.stage_index])

    def pause(self):
        self.stage_timer.pause()
        self.match_timer.pause()

    def reset_stage(self):
        self.match_timer.stop()
        self.stage_timer.reset()

    def reset_match(self):
        self.stage_index = 0
        self.stage_timer.reset()
        self.match_timer.reset()

    def run(self):
        while self.stage_index < len(self.stages):
            time.sleep(0.5)
            self.check_for_stage_change()
            self.match.time = int(self.match_timer.time())
            msg = forseti2.Time()
            msg.game_time_so_far = self.match_timer.time()
            msg.stage_time_so_far = self.stage_timer.time()
            msg.total_stage_time = self.current_stage().length
            msg.stage_name = self.current_stage().name
            self.lc.publish('Timer/Time', msg.encode())

    def handle_control(self, channel, data):
        msg = forseti2.TimeControl.decode(data)
        print('Received command', msg.command_name)
        func = {
            'pause': self.pause,
            'start': self.start,
            'reset_match': self.reset_match,
            'reset_stage': self.reset_stage
        }[msg.command_name]
        func()

    def handle_init(self, channel, data):
        msg = forseti2.Match.decode(data)
        self.match.teams = [Team(msg.team_numbers[i], msg.team_names[i]) for i in range(4)]
        self.reset()

class Team(object):

    def __init__(self, number, name=None):
        self.number = number
        if name is None:
            self.name = configurator.get_team_name(number)
        else:
            self.name = name
        self.teleop = False
        self.halt_radio = False
        self.auto = False
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled


class Match(object):

    def __init__(self, team_numbers):
        self.teams = [Team(num) for num in team_numbers]
        self.stage = 'Setup'
        self.time = 0

    def get_team(self, team_number):
        for team in self.teams:
            if team.number == team_number:
                return team

    def enable_all(self):
        for team in self.teams:
            team.enabled = True

    def disable_all(self):
        for team in self.teams:
            team.enabled = False



class ControlDataSender(Node):

    def __init__(self, lc, match, timer):
        self.lc = lc
        self.match = match
        self.timer = timer
        self.thread = threading.Thread()
        self.thread.daemon = True
        self.start_thread()
        self.seq = 0;

    def _loop(self):
        while True:
            time.sleep(0.75)
            for i in range(len(self.match.teams)):
                self.send(i + 1, self.match.teams[i])

    def send(self, piemos_num, team):
        #print('Sending')
        msg = forseti2.ControlData()
        msg.TeleopEnabled = self.match.stage in ['Teleop', 'Paused']
        msg.HaltRadio = False
        msg.AutonomousEnabled = self.match.stage == 'Autonomous'
        msg.RobotEnabled = self.timer.match_timer.running
        msg.Stage = self.match.stage
        msg.Time = self.match.time
        """
        msg = forseti2.piemos_cmd()
        msg.header = forseti2.header()
        msg.header.seq = self.seq;
        self.seq += 1;
        msg.header.time = time.time()
        msg.auton = self.match.stage == 'Autonomous'
        msg.enabled = self.timer.match_timer.running"""
        self.lc.publish('piemos/Control', msg.encode())


'''
TODO This does not appear to be used anywhere.

'''
class RemoteTimer(object):

    def __init__(self):
        self.lc = lcm.LCM(settings.LCM_URI)

    def send(self, command):
        print('Sending', command)
        msg = forseti2.TimeControl()
        msg.command_name = command
        self.lc.publish('Timer/Control', msg.encode())

    def pause(self):
        self.send('pause')

    def start(self):
        self.send('start')

    def reset_match(self):
        self.send('reset_match')

    def reset_stage(self):
        self.send('reset_stage')

def main():
    lc = lcm.LCM(settings.LCM_URI)
    match = Match([0] * 4)
    timer = MatchTimer(lc, match)
    cd_sender = ControlDataSender(lc, match, timer)
    timer.run()


if __name__ == '__main__':
    main()
