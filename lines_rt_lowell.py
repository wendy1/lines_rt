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
#rt_feeds['Fitchburg/South Acton'] = rt_feed_base_url % (api_key, 'CR-Fitchburg')
#rt_feeds['Newburyport/Rockport'] = rt_feed_base_url % (api_key, 'CR-Newburyport')
#rt_feeds['Haverhill'] = rt_feed_base_url % (api_key, 'CR-Haverhill')

deprected_feeds = dict()
deprected_feeds['Lowell'] = 'http://developer.mbta.com/lib/RTCR/RailLine_10.json'
deprected_feeds['Fitchburg/South Acton'] = 'http://developer.mbta.com/lib/RTCR/RailLine_9.json'
deprected_feeds['Newburyport/Rockport'] = 'http://developer.mbta.com/lib/RTCR/RailLine_12.json'


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
        first = True
        for linename in rt_feeds:
            if not first:
                self.prt('-------------')
            first = False

            # get real time data
            try:
                rt_info = urllib2.urlopen(rt_feeds[linename])
                rt_data = json.load(rt_info)
            except:
                self.prt('No data for %s' % (linename))
            else:
                # print trip data for each direction
                for dir in rt_data["direction"]:
                    self.prt('-- [RT] %s %s --' % (rt_data['route_name'], dir['direction_name']))

                    for trip in dir['trip']:
                        stop1 = self.get_stop_of_interest(trip)
                        if stop1:
                            pre_dt = stop1['pre_dt']
                            self.prt('- %s, vehicle %s, predicted time at %s: %s' % (trip['trip_name'], trip['vehicle']['vehicle_id'], stop1['stop_name'], todate(pre_dt)))
                        else:
                            self.prt('- %s, vehicle %s' % (trip['trip_name'], trip['vehicle']['vehicle_id']))

                    self.prt(' ')

                # print alerts for this line
                for a in rt_data['alert_headers']:
                    self.prt ('%s' % (a["header_text"]))
                if len(rt_data) > 0:
                    self.prt (' ')

            # get data from deprecated feed
            self.prt('[Deprecated feed data] ')
            if linename in deprected_feeds:
                dep_info = urllib2.urlopen(deprected_feeds[linename])
                dep_data = json.load(dep_info)

                results = dep_data['Messages']

                trip_printed = []

                for train in sorted(results, key=lambda r:r['Scheduled']):
                    trip = train['Trip']
                    if not trip in trip_printed:
                        trip_printed.append(trip)
                        destination = train['Destination']

                        # Not interested in trains bound for North Station since that's where I'm starting
                        if destination.lower() == "north station":
                            continue

                        # The scheduled time for North Station si the one we want
                        if train["Stop"].lower() != "north station":
                            continue
                        trainNumber = train['Vehicle']
                        scheduled = todate(train['Scheduled'])

                        # if scheduled < datetime.datetime.now() - datetime.timedelta(minutes=10):
                        #     continue

                        if trainNumber == '':
                            trainNumber = 'unknown'

                        self.prt("- %s Trip %s to %s, train '%s'\n" % (scheduled.strftime('%I:%M'), trip, destination, trainNumber))

                        # only print out 2 trips for each line
                        #if len(trip_printed) >= 2:
                        #    break

        return self.printlines

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

