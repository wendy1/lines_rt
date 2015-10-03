import unittest
from vehicle_list import MbtaRealTime
import re

class TestVehicleList(unittest.TestCase):

    def test_vehicle_list(self):
        print MbtaRealTime().trip_printout()

    def test_predictions_north_station_outbound(self):
        m = MbtaRealTime()
        m.printout_predictions_north_station_outbound()
        print m.printlines

    def test_find_routename(self):
        trip_id = "CR-Haverhill-CR-Weekday-Haverhill-May15-223"
        m = re.match(r'CR-([^-]+)\-', trip_id, re.M|re.I)
        self.assertEqual(m.group(1), 'Haverhill')

    def test_find_time(self):
        trip_name = "223 (8:40 pm from North Station)"
        m = re.match(r'(\d+) \((\d+:\d+)', trip_name, re.M|re.I)
        self.assertEqual(m.group(1), '223')
        self.assertEqual(m.group(2), '8:40')


# required code - this starts up the unit tests
if __name__ == '__main__':
    unittest.main()
