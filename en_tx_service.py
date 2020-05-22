import os, time
from Crypto.Random import get_random_bytes, random
from logger import *
log = Logger()

'''
This class handles the BLE Beacon Transmission (TX).
Because after some time of BLE advertising, a restart of the BLE stack (hciconfig hci0 down / up) might be required,
and because the pybleno class can't be shut down and restarted properly, the actual BLE handling has been placed
in a separate python script "en_beacon.py".
'''


class ENTxService:

    def __init__(self, bdaddr_rotation_interval_min_minutes, bdaddr_rotation_interval_max_minutes):
        self.random_bdaddr = bytes([0x00] * 6)
        self.bdaddr_rotation_interval_min_seconds = bdaddr_rotation_interval_min_minutes * 60 + 1
        self.bdaddr_rotation_interval_max_seconds = bdaddr_rotation_interval_max_minutes * 60 - 1
        if self.bdaddr_rotation_interval_max_seconds < self.bdaddr_rotation_interval_min_seconds:
            self.bdaddr_rotation_interval_max_seconds = self.bdaddr_rotation_interval_min_seconds
        self.bdaddr_next_rotation_seconds = 0

    @staticmethod
    def get_current_unix_epoch_time_seconds():
        return int(time.time())

    @staticmethod
    def get_advertising_tx_power_level():
        return 12  # in real life, this info should come from the BLE transmitter

    def roll_random_bdaddr(self):
        # Create a BLE random "Non-Resolvable Private Address", i.e. the two MSBs must be 0, and not all bits 0 or 1
        while True:
            self.random_bdaddr = bytearray(get_random_bytes(6))
            self.random_bdaddr[0] = self.random_bdaddr[0] & 0b00111111
            self.random_bdaddr = bytes(self.random_bdaddr)
            if (self.random_bdaddr.hex() != "000000000000") and (self.random_bdaddr.hex() != "3fffffffffff"):
                break
        self.bdaddr_next_rotation_seconds = (self.get_current_unix_epoch_time_seconds()
                                             + random.randint(self.bdaddr_rotation_interval_min_seconds,
                                                              self.bdaddr_rotation_interval_max_seconds))

    def bdaddr_should_roll(self):
        return self.get_current_unix_epoch_time_seconds() >= self.bdaddr_next_rotation_seconds

    def start_beacon(self, rpi, aem):
        while True:
            if os.system("python3 en_beacon.py %s %s %s" % (rpi.hex(), aem.hex(), self.random_bdaddr.hex())) == 0:
                # return code 0 means: ok, advertising started.
                break
            log.log()
            log.log("ERROR: Could not start advertising! Timestamp: %s" % time.strftime("%H:%M:%S", time.localtime()))
            log.log()
            # try to recover:
            os.system("sudo hciconfig hci0 down; sudo hciconfig hci0 up")
            time.sleep(1)

    @staticmethod
    def stop_beacon():
        os.system("sudo hciconfig hci0 down; sudo hciconfig hci0 up")
