#!/usr/bin/env python2.7
from __future__ import print_function

import argparse
import time
import csv
import lcm
import os
import os.path

from forseti2 import *

config_dir = '../configs'
team_nums_to_names = {}
team_csv_filename = '../resources/teams.csv'

def init_team_nums():
    team_reader = csv.reader(open(team_csv_filename))
    for row in team_reader:
        team_nums_to_names[int(row[0])] = row[1]
init_team_nums()

def main():
    lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')
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

def do_config(lc, teams, field_map_filename='../resources/field_mapping.json'):
    field_objects = '[]'
    with open(field_map_filename, 'r') as rfile:
        field_objects = rfile.read()
    #print('Field map', field_objects)
    for i in range(len(teams)):
        send_team_config(lc, teams[i], i+1, field_objects)

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
    data.ConfigFile = get_config(num)
    data.IsBlueAlliance = idx <= 2
    data.TeamNumber = int(num)
    data.TeamName = get_team_name(num)
    data.FieldObjects = field_objects
    data.header = forseti2.header()
    data.header.seq = 0
    data.header.time = time.time()
    lc.publish('PiEMOS' + str(idx) + '/Config', data.encode())

def send_team_reset(lc, num, idx):
    data = CommandData()
    data.command = 'Reset'
    data.header = forseti2.header()
    data.header.seq = 0
    data.header.time = time.time()
    lc.publish('PiEMOS' + str(idx) + '/Command', data.encode())


if __name__ == '__main__':
    main()
