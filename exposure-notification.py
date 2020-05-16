#!/usr/bin/env python3
from en_tx_service import *
from en_tx_data_store import *
from en_rx_service import *
from en_rx_data_store import *
from en_crypto import *
import time
import argparse


'''
Exposure Notification BLE Simulator

This script transmits, and scans for and records 'Exposure Notification' Beacons according to
https://blog.google/inside-google/company-announcements/apple-and-google-partner-covid-19-contact-tracing-technology/
https://blog.google/documents/70/Exposure_Notification_-_Bluetooth_Specification_v1.2.2.pdf
https://blog.google/documents/69/Exposure_Notification_-_Cryptography_Specification_v1.2.1.pdf

Transmission is handled in en_tx_service.py.
Scanning is handled in en_rx_service.py.
Cryptography is handled in en_crypto.py.
'''


def get_current_unix_epoch_time_seconds():
    return int(time.time())


try:
    parser = argparse.ArgumentParser(description="Exposure Notification BLE Simulator.")
    parser.add_argument("-t", "--triggertx",
                        help="trigger TX again after RX, if the Linux kernel wasn't patched to allow both in parallel",
                        action="store_true")
    parser.add_argument("-c", "--cycletime", type=int, default=5*60,
                        help="duration (in seconds) of one cycle")
    parser.add_argument("-s", "--scantime", type=int, default=2,
                        help="duration (in seconds) of the scanning within one cycle")
    args = parser.parse_args()
    trigger_tx = args.triggertx
    total_scan_time_seconds = args.scantime
    total_cycle_time_seconds = max(args.cycletime, total_scan_time_seconds)

    print("Exposure Notification BLE Simulator")
    print("This script simulates an 'Exposure Notification V1.2'-enabled device.")

    one_scan_interval_seconds = 2
    num_scan_intervals = -(-total_scan_time_seconds // one_scan_interval_seconds)  # ceil division
    sleep_time_seconds = max(total_cycle_time_seconds - num_scan_intervals * one_scan_interval_seconds, 0)
    rx_list_filter_time_seconds = 2 * total_cycle_time_seconds + 10
    print("\nFull cycle duration: %ds, thereof scanning duration: %ds" %
          (sleep_time_seconds + num_scan_intervals * one_scan_interval_seconds,
           num_scan_intervals * one_scan_interval_seconds))

    tx_data_store = ENTxDataStore("tek_data.csv")
    rx_data_store = ENRxDataStore("rx_raw_data.csv", "rx_data.csv", rx_list_filter_time_seconds)

    crypto = ENCrypto(interval_length_minutes=10, tek_rolling_period=144)

    tx_service = ENTxService(bdaddr_rotation_interval_min_minutes=10, bdaddr_rotation_interval_max_minutes=20)
    ble_advertising_tx_power_level = tx_service.get_advertising_tx_power_level()
    rx_service = ENRxService()

    while True:
        if crypto.tek_should_roll():
            print("\nTX: TEK should roll...")
            crypto.roll_tek()
            tx_data_store.write(crypto.tek_roll_interval_i, crypto.tek)
            crypto.derive_keys()

        if tx_service.bdaddr_should_roll():
            print("\nTX: BDADDR should roll...")
            tx_service.stop_beacon()
            tx_service.roll_random_bdaddr()
            # also create new RPI and encrypt metadata again:
            crypto.encrypt_rpi()
            crypto.encrypt_aem(metadata=[0x40, ble_advertising_tx_power_level, 0x00, 0x00], rpi=crypto.rpi)
            tx_service.start_beacon(rpi=crypto.rpi, aem=crypto.aem)
        elif trigger_tx:
            tx_service.start_beacon(rpi=crypto.rpi, aem=crypto.aem)

        for _ in range(sleep_time_seconds):
            print(".", end='', flush=True)
            time.sleep(1)

        print("\nBLE RX: Now scanning...")

        timestamp = get_current_unix_epoch_time_seconds()
        for _ in range(num_scan_intervals):
            timestamp = get_current_unix_epoch_time_seconds()
            scan_result = rx_service.scan(t=one_scan_interval_seconds)
            for beacon in scan_result:
                rx_data_store.write(beacon, timestamp)
        rx_data_store.filter_rx_list(timestamp)

except KeyboardInterrupt:
    print("\nKeyboard Interrupt.")
