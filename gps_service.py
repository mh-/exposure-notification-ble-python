import threading
import time
import gps
import datetime


class GpsMessageHandler(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.gps_data = gps.gps(mode=gps.WATCH_ENABLE)
        self.date_time = None
        self.lat = None
        self.lon = None
        self.altitude = None
        self.speed = None
        self.daemon = True  # stop this thread when the main thread ends
        self.start()  # now start polling for gpsd messages

    def get_date_time(self):  # Note: This could be old. But if it's not None, it was at least previously valid.
        return self.date_time

    def get_pos(self):
        return self.lat, self.lon, self.altitude

    def get_speed(self):
        return self.speed

    def run(self):
        try:
            while True:
                gps_data = self.gps_data.next()
                if gps_data:
                    if "time" in gps_data:
                        # get time from GPS, add "+0000" to import it as UTC
                        date_time_utc = datetime.datetime.strptime(gps_data["time"]+"+0000", "%Y-%m-%dT%H:%M:%S.%fZ%z")
                        # Convert to local time
                        self.date_time = date_time_utc.astimezone(datetime.datetime.utcnow().astimezone().tzinfo).\
                            strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                    if "lat" in gps_data and "lon" in gps_data:
                        self.lat = gps_data["lat"]
                        self.lon = gps_data["lon"]
                        if "alt" in gps_data:
                            self.altitude = gps_data["alt"]
                        else:
                            self.altitude = None
                    if "speed" in gps_data:
                        self.speed = gps_data["speed"]
                time.sleep(0.1)
        except StopIteration:
            pass


if __name__ == '__main__':

    gps_handler = GpsMessageHandler()
    while True:
        # print current values for test purposes
        time.sleep(5)
        print("Time: %s - LAT, LON, Altitude: %s - Speed: %f" % (gps_handler.get_date_time(), gps_handler.get_pos(), gps_handler.get_speed()))
