import sys

__author__ = 'wswanbeck'
import json
import urllib
import urllib2
import datetime
import re

def todate(datestring):
    return datetime.datetime.fromtimestamp(int(datestring))

api_key = 'jfhKC8TLdkWIsOs-DVEUGg'

rt_predictions_by_routes = dict()
rt_feed_base_url = 'http://realtime.mbta.com/developer/api/v2/predictionsbyroute?api_key=%s&route=%s&format=json'
rt_predictions_by_routes['Lowell'] = rt_feed_base_url % (api_key, 'CR-Lowell')
rt_predictions_by_routes['Fitchburg/South Acton'] = rt_feed_base_url % (api_key, 'CR-Fitchburg')
rt_predictions_by_routes['Newburyport/Rockport'] = rt_feed_base_url % (api_key, 'CR-Newburyport')
rt_predictions_by_routes['Haverhill'] = rt_feed_base_url % (api_key, 'CR-Haverhill')

rt_predictions_by_stop_north_station = 'http://realtime.mbta.com/developer/api/v2/predictionsbystop?api_key=%s&format=json&stop=%s' % (api_key, '''North%20Station''')

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
            rt_info = urllib2.urlopen(rt_predictions_by_routes[linename])
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

        # get predictions for outbound north station routes
        self.printout_predictions_north_station_outbound()

        return self.printlines

    def printout_predictions_north_station_outbound(self):
        # get predictions for north station
        try:
            pred_out_json = urllib2.urlopen(rt_predictions_by_stop_north_station)
            pred_out = json.load(pred_out_json)
        except Exception as ex:
            self.prt("--- Can't get North Station outbound prediction data")
        else:
            self.prt('--- North Station outbound predictions')
            routes = pred_out['mode'][0]['route']

            for route in routes:
                for direction in route['direction']:
                    if direction['direction_id'] != '0': # 0 is outbound - that's all we care about here
                        continue
                    for trip in direction['trip']:

                        # get trip name out of trip_id (e.g. get Haverhill out of "CR-Haverhill-CR-Weekday-Haverhill-May15-223"
                        m = re.match(r'CR-([^-]+)\-', trip['trip_id'], re.M|re.I)
                        destname = m.group(1)

                        # get trip number and departure time out of trip_name (e.g. get '223' and '8:40' out of "223 (8:40 pm from North Station)"
                        m = re.match(r'(\d+) \((\d+:\d+)', trip['trip_name'], re.M|re.I)
                        trip_number = m.group(1)
                        departure_time = m.group(2)

                        self.prt('%s-%s (%s)' % (destname, trip_number, departure_time))
                        vehicle = '?'
                        if 'vehicle' in trip:
                            vehicle = trip['vehicle']['vehicle_id']

                        arriving_in = ''
                        if 'pre_away' in trip:
                            arriving_in = 'arriving at NS in %s seconds' % trip['pre_away']

                        self.prt('  #%s %s'% (vehicle, arriving_in))

if __name__ == '__main__':

    try:
        import androidhelper
        droid = androidhelper.Android()

        while True:
            response = droid.dialogGetInput("Next Trips", MbtaRealTime().trip_printout())
            if response.result is None:
                break
    except:
        print MbtaRealTime().trip_printout()
