#!/usr/bin/python

# Copyright 2017 Chris Gheen
#
#

import pickle
import pycarwings2
import logging
import pprint
import argparse
import sys
import os.path

class Carwings:
    def __init__(self, username, password, region):
        try:
            self.session = pycarwings2.Session(username, password, region)
            self.leaf = self.session.get_leaf()
        except:
            pass

    def battery_percent(self):
        st = self.leaf.get_latest_battery_status()
        return "{0}|{1}|{2}".format(st.battery_percent, st.plugin_state, st.charging_status)

    def request_update(self):
        return self.leaf.request_update()

    def _get_update(self, result):
        try:
            status = self.leaf.get_status_from_update(result)
            if status == None:
                return None
            return "{0}|{1}|{2}".format(status.battery_percent, status.plugin_state, status.charging_status)
        except pycarwings2.CarwingsError:
            return "Could not establish communications with vehicle."

    def get_update(self):
        return _get_update(self.result_key)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Your Nissan Connect username")
    parser.add_argument("-p", "--password", help="Your Nissan Connect password")
    parser.add_argument("-r", "--region", help="Your Region Code")
    parser.add_argument("-c", "--command", help="command to run")
    parser.add_argument("-a", "--argument", help="the parameter for the command")
    parser.add_argument("-d", '--debug', dest='debug', action='store_true')

    args = parser.parse_args()

    if args.username == None or args.password == None or args.region == None:
        parser.print_help()
        exit(0)

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    
    cmd = None    

    if os.path.isfile('carwings.pk'):
        output = open('carwings.pk', 'rb')
        cmd = pickle.load(output)
        output.close()
    else:    
        cmd = Carwings(args.username, args.password, args.region)
    
    if args.command == "result":
        print(cmd._get_update(args.argument))
        #print(cmd._get_update("BAXCiGNDKZfL44ReAvlmv7SDVHIk02bcdZElF2O01UmVydaYzl"))
    elif args.command == "update":
        print(cmd.request_update())

    else:
        print(cmd.battery_percent())

    save = open('carwings.pk', 'wb')
    pickle.dump(cmd, save)
    save.close()

            
main()
