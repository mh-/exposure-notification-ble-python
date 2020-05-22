class ENRxDataStore:
    def __init__(self, rx_raw_data_file_name, rx_processed_data_filename, filter_time_seconds, store_raw_data,
                 store_gps_position):
        self.store_raw_data = store_raw_data
        self.store_gps_position = store_gps_position
        if self.store_raw_data:
            self.rx_raw_data_file = open(rx_raw_data_file_name, 'a')
            self.rx_raw_data_file.write("Time;RPI;AEM;RSSI;BDADDR")
            if self.store_gps_position:
                self.rx_raw_data_file.write(";LAT;LON;Altitude;Speed")
            self.rx_raw_data_file.write("\n")
        self.rx_data_file = open(rx_processed_data_filename, 'a')
        self.rx_data_file.write("StartTime;EndTime;RPI;AEM;MaxRSSI;BDADDR")
        if self.store_gps_position:
            self.rx_data_file.write(";LAT;LON;Altitude;Speed")
        self.rx_data_file.write("\n")
        self.rx_dict = dict()
        self.filter_time_seconds = filter_time_seconds

    def __del__(self):
        if self.store_raw_data:
            self.rx_raw_data_file.close()
        for key in self.rx_dict:
            beacon_values = self.rx_dict[key]
            self.write_filtered_list(key, beacon_values)
        self.rx_data_file.close()

    def consider_in_rx_list(self, beacon, timestamp, gps_lat=None, gps_lon=None, gps_altitude=None, gps_speed=None):
        if beacon.rpi in self.rx_dict:
            # Found RPI in list: keep start_timestamp
            start_timestamp = self.rx_dict[beacon.rpi][3]
            previous_max_rssi = self.rx_dict[beacon.rpi][1]
            if not self.store_gps_position:
                self.rx_dict[beacon.rpi] = [beacon.aem, max(previous_max_rssi, beacon.rssi), beacon.bdaddr,
                                            start_timestamp, timestamp]
            else:
                self.rx_dict[beacon.rpi] = [beacon.aem, max(previous_max_rssi, beacon.rssi), beacon.bdaddr,
                                            start_timestamp, timestamp,
                                            gps_lat, gps_lon, gps_altitude, gps_speed]
        else:
            # New RPI: store now
            if not self.store_gps_position:
                self.rx_dict[beacon.rpi] = [beacon.aem, beacon.rssi, beacon.bdaddr, timestamp, timestamp]
            else:
                self.rx_dict[beacon.rpi] = [beacon.aem, beacon.rssi, beacon.bdaddr, timestamp, timestamp,
                                            gps_lat, gps_lon, gps_altitude, gps_speed]

    def filter_rx_list(self, current_timestamp):
        old_beacon_keys = [key for (key, value) in self.rx_dict.items()
                           if current_timestamp - value[4] >= self.filter_time_seconds]
        for key in old_beacon_keys:
            beacon_values = self.rx_dict.pop(key)
            self.write_filtered_list(key, beacon_values)

    def write_filtered_list(self, key, beacon_values):
        self.rx_data_file.write("%d;%d;%s;%s;%d;%s" %
                                (beacon_values[3], beacon_values[4], key.hex(), beacon_values[0].hex(),
                                 beacon_values[1], beacon_values[2]))
        if self.store_gps_position:
            self.rx_data_file.write(";%s;%s;%s;%s" %
                                    (beacon_values[5], beacon_values[6], beacon_values[7], beacon_values[8]))
        self.rx_data_file.write("\n")
        self.rx_data_file.flush()
        print("BLE RX: Beacon was received for %d seconds: RPI: %s, AEM: %s, max. RSSI: %d, BDADDR: %s" %
              (beacon_values[4] - beacon_values[3], key.hex(), beacon_values[0].hex(), beacon_values[1],
               beacon_values[2]))

    def write(self, beacon, current_timestamp, gps_lat=None, gps_lon=None, gps_altitude=None, gps_speed=None):
        if self.store_raw_data:
            self.rx_raw_data_file.write("%d;%s;%s;%d;%s" %
                                   (current_timestamp, beacon.rpi.hex(), beacon.aem.hex(), beacon.rssi, beacon.bdaddr))
            if self.store_gps_position:
                self.rx_raw_data_file.write(";%s;%s;%s;%s" % (gps_lat, gps_lon, gps_altitude, gps_speed))
            self.rx_raw_data_file.write("\n")
        self.consider_in_rx_list(beacon, current_timestamp,
                                 gps_lat=gps_lat, gps_lon=gps_lon, gps_altitude=gps_altitude, gps_speed=gps_speed)
