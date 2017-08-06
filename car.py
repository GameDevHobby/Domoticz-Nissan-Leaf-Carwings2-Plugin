#!/usr/bin/python

# Copyright 2017 Chris Gheen
#
#

import pycarwings2
import logging
import pprint
import argparse
import sys

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

class Carwings:
    def __init__(self, username, password, region):
        self.session = pycarwings2.Session(username, password, region)
        self.leaf = self.session.get_leaf()
        self.latestStatus = self.leaf.get_latest_battery_status()

    def battery_percent(self):
        st = self.latestStatus
        return "{0}|{1}|{2}".format(st.battery_percent, st.plugin_state, st.charging_status)


"""
print "Login..."
l = s.get_leaf()

print "get_latest_battery_status"
leaf_info = l.get_latest_battery_status()
print "date %s" % leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"]
print "date %s" % leaf_info.answer["BatteryStatusRecords"]["NotificationDateAndTime"]
print "battery_capacity2 %s" % leaf_info.answer["BatteryStatusRecords"]["BatteryStatus"]["BatteryCapacity"]

print "battery_capacity %s" % leaf_info.battery_capacity
print "charging_status %s" % leaf_info.charging_status
print "battery_capacity %s" % leaf_info.battery_capacity
print "battery_remaining_amount %s" % leaf_info.battery_remaining_amount
print "charging_status %s" % leaf_info.charging_status
print "is_charging %s" % leaf_info.is_charging
print "is_quick_charging %s" % leaf_info.is_quick_charging
print "plugin_state %s" % leaf_info.plugin_state
print "is_connected %s" % leaf_info.is_connected
print "is_connected_to_quick_charger %s" % leaf_info.is_connected_to_quick_charger
print "time_to_full_trickle %s" % leaf_info.time_to_full_trickle
print "time_to_full_l2 %s" % leaf_info.time_to_full_l2
print "time_to_full_l2_6kw %s" % leaf_info.time_to_full_l2_6kw
print "leaf_info.battery_percent %s" % leaf_info.battery_percent


result_key = l.request_update()
print "start sleep 10"
time.sleep(10) # sleep 60 seconds to give request time to process
print "end sleep 10"
battery_status = l.get_status_from_update(result_key)
while battery_status is None:
	print "not update"
        time.sleep(10)
	battery_status = l.get_status_from_update(result_key)

pprint.pprint(battery_status.answer)

#pprint.pprint(l.get_driving_analysis())

#pprint.pprint(l.get_latest_hvac_status())

#result_key = l.start_climate_control()
#time.sleep(60)
#start_cc_result = l.get_start_climate_control_result(result_key)

#result_key = l.stop_climate_control()
#time.sleep(60)
#stop_cc_result = l.get_stop_climate_control_result(result_key)
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Your Nissan Connect username")
    parser.add_argument("-p", "--password", help="Your Nissan Connect password")
    parser.add_argument("-r", "--region", help="Your Region Code")
        
    args = parser.parse_args()

    if args.username == None or args.password == None or args.region == None:
        parser.print_help()
        exit(0)

    cmd = Carwings(args.username, args.password, args.region)
    
    print(cmd.battery_percent())

    """
    if(args.command):
        print(cmd.run(args.command, args.arg))
    else:
        cmd.check()
        print("TV is on.")
    """


            
main()
