class ENRxDataStore:
    def __init__(self, rx_raw_data_file_name, rx_processed_data_filename):
        self.rx_raw_data_file = open(rx_raw_data_file_name, 'a')
        self.rx_raw_data_file.write("Time;RPI;AEM;RSSI;BDADDR\n")
        self.rx_data_file = open(rx_processed_data_filename, 'a')
        self.rx_data_file.write("StartTime;EndTime;RPI;AEM;MaxRSSI;BDADDR\n")
        self.rx_dict = dict()

    def __del__(self):
        self.rx_raw_data_file.close()
        for key in self.rx_dict:
            beacon_values = self.rx_dict[key]
            self.rx_data_file.write("%d;%d;%s;%s;%d;%s\n" %
                                        (beacon_values[3], beacon_values[4], key.hex(), beacon_values[0].hex(),
                                         beacon_values[1], beacon_values[2]))
            print("BLE RX: Beacon was received for %d seconds: RPI: %s, AEM: %s, max. RSSI: %d, BDADDR: %s" %
                  (beacon_values[4] - beacon_values[3], key.hex(), beacon_values[0].hex(), beacon_values[1],
                   beacon_values[2]))
        self.rx_data_file.close()

    def consider_in_rx_list(self, beacon, timestamp):
        if beacon.rpi in self.rx_dict:
            start_timestamp = self.rx_dict[beacon.rpi][3]
            previous_max_rssi = self.rx_dict[beacon.rpi][1]
            self.rx_dict[beacon.rpi] = [beacon.aem, max(previous_max_rssi, beacon.rssi), beacon.bdaddr,
                                        start_timestamp, timestamp]
        else:
            self.rx_dict[beacon.rpi] = [beacon.aem, beacon.rssi, beacon.bdaddr, timestamp, timestamp]

    def filter_rx_list(self, current_timestamp):
        old_beacon_keys = [key for (key, value) in self.rx_dict.items() if current_timestamp - value[4] >= 10]
        for key in old_beacon_keys:
            beacon_values = self.rx_dict.pop(key)
            self.rx_data_file.write("%d;%d;%s;%s;%d;%s\n" %
                                        (beacon_values[3], beacon_values[4], key.hex(), beacon_values[0].hex(),
                                         beacon_values[1], beacon_values[2]))
            print("\nBLE RX: Beacon was received for %d seconds: RPI: %s, AEM: %s, max. RSSI: %d, BDADDR: %s" %
                  (beacon_values[4]-beacon_values[3], key.hex(), beacon_values[0].hex(), beacon_values[1],
                   beacon_values[2]))
        self.rx_data_file.flush()

    def write(self, beacon, current_timestamp):
        self.rx_raw_data_file.write("%d;%s;%s;%d;%s\n" %
                               (current_timestamp, beacon.rpi.hex(), beacon.aem.hex(), beacon.rssi, beacon.bdaddr))
        self.rx_raw_data_file.flush()
        self.consider_in_rx_list(beacon, current_timestamp)
