#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
configurator.py
Created on Sat Apr  27 12:00:00 2013

@author: kyle

reads from various resource files stored on disk.
sends configs to PiEMOS controller, via channels PiEMOS{n}/Config
these configs contain RFID mappings and the PiEMOS layout configuration.

example usage:
    python configurator.py --teams 100,14,19,25
                            --load ../resources/field_mapping.json
                            --config


"""


from __future__ import print_function

import argparse
import csv
import lcm
import os
import os.path
import time

from forseti2 import *
import settings

config_dir = '../configs'
team_nums_to_names = {}
team_csv_filename = '../resources/teams.csv'

def init_team_nums():
    team_reader = csv.reader(open(team_csv_filename))
    for row in team_reader:
        team_nums_to_names[int(row[0])] = row[1]
init_team_nums()

def main():
    lc = lcm.LCM(settings.LCM_URI)
    parser = argparse.ArgumentParser()
    parser.add_argument('--load', type=str, action='store')
    parser.add_argument('--teams', type=str, action='store')
    parser.add_argument('--config', const=True, action='store_const')
    parser.add_argument('--reset', const=True, action='store_const')
    args = parser.parse_args()
    teams = []
    try:
        teams = list(map(int, args.teams.split(',')))
    except ValueError:
        print('Could not parse team list.')
        print('Please send a comma-separated list of numbers.')
    if args.config:
        do_config(lc, teams, args.load)
    if args.reset:
        do_reset(lc, args, teams)

def do_reset(lc, args, teams):
    print('Resetting')
    for i in range(len(teams)):
        send_team_reset(lc, teams[i], i + 1)

def do_config(lc, teams, gold_field_map_filename='../resources/smallfieldmap.json', blue_field_map_filename='../resources/smallfieldmap.json'):
    gold_field_objects = '[]'
    try:
        with open(gold_field_map_filename, 'r') as rfile:
            gold_field_objects = rfile.read()
    except Exception as ex:
        print(ex)
        gold_field_objects = '[]'
    blue_field_objects = '[]'
    try:
        with open(blue_field_map_filename, 'r') as rfile:
            blue_field_objects = rfile.read()
    except Exception as ex:
        print(ex)
        gold_field_objects = '[]'
    #print('Field map', field_objects)
    gold_teams = len(teams)/2
    for i in range(len(teams)):
        time.sleep(1)
        if (i >= gold_teams):
            send_team_config(lc, teams[i], i, gold_field_objects)
        else:
            send_team_config(lc, teams[i], i, blue_field_objects)

def get_default_config():
    try:
        with open(os.path.join(config_dir, 'default.cfg'), 'r') as rfile:
            default_config = rfile.read()
            #print('Default config:', default_config)
            return default_config
    except IOError as e:
        print('Could not get default config.')
        raise e

def get_config(num):
    try:
        with open(os.path.join(config_dir, '{}.cfg'.format(num)),
                  'r') as rfile:
            config = rfile.read()
            if config == '':
                return get_default_config()
            #print('Team {} config:'.format(num), config)
            return config
    except IOError:
        print('Could not get config for team {}'.format(num))
        return get_default_config()

def get_team_name(num):
    return team_nums_to_names.get(num, 'Unknown Team')

def send_team_config(lc, num, idx, field_objects):
    data = ConfigData()
    match = match_data()
    data.ConfigFile = get_config(num).replace('\t','').replace('\n', '').replace('\r', '')
    match.IsBlueAlliance = idx <= 1
    data.TeamNumber = int(num)
    match.TeamNumber = int(num)
    match.TeamName = get_team_name(num)
    match.FieldObjects = field_objects.replace('\t','').replace('\n', '').replace('\r', '')
    lc.publish('PiEMOS' + str(idx) + '/Config', data.encode())
    time.sleep(1)
    lc.publish('piemos' + str(idx) + '/match', match.encode())

def send_team_reset(lc, num, idx):
    data = CommandData()
    data.command = 'Reset'
    lc.publish('PiEMOS' + str(idx) + '/Command', data.encode())


if __name__ == '__main__':
    main()
