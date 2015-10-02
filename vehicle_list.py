import sys

__author__ = 'wswanbeck'
import json
import urllib2
import datetime

def todate(datestring):
    return datetime.datetime.fromtimestamp(int(datestring))

api_key = 'jfhKC8TLdkWIsOs-DVEUGg'

rt_feeds = dict()
rt_feed_base_url = 'http://realtime.mbta.com/developer/api/v2/predictionsbyroute?api_key=%s&route=%s&format=json'
rt_feeds['Lowell'] = rt_feed_base_url % (api_key, 'CR-Lowell')
rt_feeds['Fitchburg/South Acton'] = rt_feed_base_url % (api_key, 'CR-Fitchburg')
rt_feeds['Newburyport/Rockport'] = rt_feed_base_url % (api_key, 'CR-Newburyport')
rt_feeds['Haverhill'] = rt_feed_base_url % (api_key, 'CR-Haverhill')

deprected_feeds = dict()
deprected_feeds['Lowell'] = 'http://developer.mbta.com/lib/RTCR/RailLine_10.json'
deprected_feeds['Haverill'] = 'http://developer.mbta.com/lib/RTCR/RailLine_11.json'
deprected_feeds['Fitchburg/South Acton'] = 'http://developer.mbta.com/lib/RTCR/RailLine_9.json'
deprected_feeds['Newburyport/Rockport'] = 'http://developer.mbta.com/lib/RTCR/RailLine_12.json'


class VehicleInfo:
    def __init__(self, line, tripnumber):
        self.line = line
        self.tripnumber = tripnumber


class MbtaRealTime:
    def __init__(self):
        self.printlines = ''

    def prt(self, s):
        self.printlines = self.printlines + '\n%s' % s

    def get_stop_of_interest(self, trip):
        highest_stop = None
        highest_stop_number = 0

        for stop in trip['stop']:
            # if we have a stop #1, return it
            seq = stop['stop_sequence']
            if seq == '1':
                return stop

            # otherwise, save the highest stop
            if int(seq) > highest_stop_number:
                highest_stop_number = int(seq)
                highest_stop = stop

        return highest_stop

    def trip_printout(self):
        trains = {}
        for line in deprected_feeds.keys():
            rt_data = ''
            feed_url = deprected_feeds[line]
            try:
                rt_info = urllib2.urlopen(feed_url)
                rt_data = json.load(rt_info)
                pass
            except:
                self.prt('No data for %s' % (feed_url))
            else:
                for m in rt_data["Messages"]:
                    trains[m["Vehicle"]] = VehicleInfo(line, m["Trip"])

        vs = trains.keys()
        vs.sort()
        for v in vs:
            if v is None or len(v) == 0:
                continue

            t = trains[v]
            self.prt("#%s %s_%s" % (v, t.line, t.tripnumber))

        # real time data for Lowell
        linename = "Lowell"

        # get real time data
        try:
            rt_info = urllib2.urlopen(rt_feeds[linename])
            rt_data = json.load(rt_info)
        except:
            self.prt('No [RT] data for %s' % (linename))
        else:
            # print trip data for each direction
            self.prt(' ')
            for dir in rt_data["direction"]:
                self.prt('-- [RT] %s %s --' % (rt_data['route_name'], dir['direction_name']))

                for trip in dir['trip']:
                    stop1 = self.get_stop_of_interest(trip)
                    if stop1:
                        pre_dt = stop1['pre_dt']
                        vehicle_id = "?"
                        if 'vehicle' in trip:
                            vehicle_id = trip['vehicle']['vehicle_id']

                        self.prt('- %s, vehicle %s, predicted time at %s: %s' % (trip['trip_name'], vehicle_id, stop1['stop_name'], todate(pre_dt)))
                    else:
                        self.prt('- %s, vehicle %s' % (trip['trip_name'], trip['vehicle']['vehicle_id']))

                self.prt(' ')

            # print alerts for this line
            for a in rt_data['alert_headers']:
                self.prt ('%s' % (a["header_text"]))
            if len(rt_data) > 0:
                self.prt (' ')

        return self.printlines

if __name__ == '__main__':
    for arg_entry in enumerate(sys.argv):
        arg_num = arg_entry[0]
        arg = arg_entry[1]
        # if arg_num == 0:        # This script
        #     pass
        # elif arg == '--printout':
        #     print MbtaRealTime().trip_printout()
        #     exit()

    try:
        import androidhelper
        droid = androidhelper.Android()

        while True:
            response = droid.dialogGetInput("Next Trips", MbtaRealTime().trip_printout())
            if response.result is None:
                break
    except:
        print MbtaRealTime().trip_printout()
