#!/usr/bin/env python3

# This script activates an Exposure Notification V1.2 BLE Beacon.
# To disable the beacon again, this can be used:
#    os.system("sudo hciconfig hci0 down; sudo hciconfig hci0 up")

from pybleno import *
from pybleno.hci_socket.BluetoothHCI import *
import struct, sys, time
import argparse


class ENBeacon(BlenoPrimaryService):

    def __init__(self, rpi, aem, bdaddr, uuid=0xFD6F):
        BlenoPrimaryService.__init__(self, {"uuid":"{:04x}".format(uuid)})
        self.bleno = Bleno()
        self.uuid = struct.pack("<H", uuid)
        self.rpi = rpi
        self.aem = aem
        self.random_bdaddr = bdaddr
        self.advertising_tx_power_level = 10
        self.bleno.on("advertisingStart", self.on_advertising_start)
        self.bleno.on("advertisingStop", self.on_advertising_stop)
        self.bleno.on("advertisingChannelTxPowerUpdate", self.on_advertising_channel_tx_power_level_update)

        self.set_en_advertising_parameters()  # this will be successful only before bleno is poweredOn.

        # print("BLE TX: Starting Bleno...")
        self.bleno.start()
        self.bleno.readAdvertisingChannelTxPowerLevel()
        self.set_advertising_bdaddr()
        self.start()

    def on_advertising_start(self, error):
        if not error:
            print("BLE TX: OK, we are advertising.")
        else:
            print("BLE TX: ERROR, could not start advertising.")
            sys.exit(0)

    def on_advertising_stop(self):
        print("BLE TX: Advertising was stopped.")

    def start(self):
        while not self.bleno.state == "poweredOn":
            pass  # Advertising must be started only after bleno is poweredOn.
        print("BLE TX: Power is on, now starting to advertise...")
        self.start_advertising(self.uuid, self.rpi, self.aem)

    def stop(self):
        print("BLE TX: Stopping...")
        self.bleno.stopAdvertising()

    def set_en_advertising_parameters(self):
        # Note: The Advertising_Interval_Min and Advertising_Interval_Max shall not be set to less than 0x00A0 (100 ms)
        # if the Advertising_Type is set to 0x02 (ADV_SCAN_IND) or 0x03 (ADV_NONCONN_IND).
        self.bleno.setAdvertisingParams(advertisementIntervalMin=200 * 1000 // 625,
                                        advertisementIntervalMax=270 * 1000 // 625,
                                        adv_type=ADV_NONCONN_IND, own_addr_type=LE_RANDOM_ADDRESS,
                                        direct_addr_type=LE_PUBLIC_ADDRESS, direct_addr=[],  # not relevant
                                        adv_channel_map=0x07,  # this defines on which channel we advertise
                                        adv_filter_policy=FILTER_POLICY_NO_WHITELIST)  # not relevant

    def start_advertising(self, uuid, rpi, aem):
        # To have full control over the advertising packets, we specify EIR (Extended Inquiry Response)
        # EIR Format is: Length, Data Type, Data (in little-endian byte order), 31 bytes
        # If the EIR is shorter than 31 bytes, add 0x00 bytes padding at the end.
        # For EIR Data Types: see https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile/
        # - Flags Section: 0201 1a
        # - Complete List of 16-bit Service Class UUIDs: 0303 6ffd
        # - Service Data (16-bit UUID, 20 bytes): 1716 6ffd <RPI> <AEM>
        # see also ExposureNotification-FrameworkDocumentationv1.2.pdf "Advertising Payload"
        # advertisement_data = bytes.fromhex("020102") + \
        advertisement_data = bytes.fromhex("02011a") + \
                             bytes.fromhex("0303") + bytes(uuid) + \
                             bytes.fromhex("1716") + bytes(uuid) + bytes(rpi) + bytes(aem)
        self.bleno.startAdvertisingWithEIRData(advertisementData=advertisement_data, scanData=[],
                                               callback=None)

    def set_advertising_bdaddr(self):
        # print("BLE TX: Setting advertising random bdaddr to %s." % bytes(self.random_bdaddr).hex())
        self.bleno.setRandomAddress(self.random_bdaddr)

    def on_advertising_channel_tx_power_level_update(self, tx_power_level):
        print("BLE TX: Read Advertising Channel TX Power Level: %d dBm" % tx_power_level)
        self.advertising_tx_power_level = tx_power_level


parser = argparse.ArgumentParser(description="Simulate an Exposure Notification V1.2 BLE Beacon.")
parser.add_argument("rpi_string", metavar="RPI", help="the desired RPI value (16 bytes hex string)")
parser.add_argument("aem_string", metavar="AEM", help="the desired AEM value (4 bytes hex string)")
parser.add_argument("bdaddr_string", metavar="BDADDR", help="the random BDADDR (6 bytes hex string)")

args = parser.parse_args()

try:
    _rpi = bytes.fromhex(args.rpi_string)
    if len(_rpi) != 16:
        raise ValueError
except ValueError:
    parser.error("ERROR: RPI must be exactly 16 bytes!")
try:
    _aem = bytes.fromhex(args.aem_string)
    if len(_aem) != 4:
        raise ValueError
except ValueError:
    parser.error("ERROR: AEM must be exactly 4 bytes!")
try:
    _bdaddr = bytes.fromhex(args.bdaddr_string)
    if len(_bdaddr) != 6:
        raise ValueError
except ValueError:
    parser.error("ERROR: BDADDR must be exactly 6 bytes!")
# noinspection PyUnboundLocalVariable
if (_bdaddr[0] & 0b11000000) != 0:
    parser.error("ERROR: The two MSBs of BDADDR must be 0, because we need a Non-Resolvable Private Address!")
    # Note: If the two MSBs are 0b10 (undefined address type), iOS will discard the advertisement!
if (_bdaddr.hex() == "000000000000") or (_bdaddr.hex() == "3fffffffffff"):
    parser.error("ERROR: BDADDR must not be all 0 or all 1!")

print("BLE TX: RPI: %s, AEM: %s, BDADDR: %s" % (args.rpi_string, args.aem_string, args.bdaddr_string))
# noinspection PyUnboundLocalVariable
beacon = ENBeacon(rpi=_rpi, aem=_aem, bdaddr=_bdaddr)
time.sleep(0.2)
sys.exit(0)
