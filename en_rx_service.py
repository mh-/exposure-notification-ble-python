from bluepy import btle
from bluepy.btle import ScanEntry
from logger import *
log = Logger()

''' 
This class handles the BLE scanning.
'''


class ENBeaconRx:
    def __init__(self, rpi, aem, rssi, bdaddr):
        self.rpi = rpi
        self.aem = aem
        self.rssi = rssi
        self.bdaddr = bdaddr


class ENRxService:

    def __init__(self, iface=0):
        self.scanner = btle.Scanner(iface)

    def scan(self, t=1):
        # log.log("BLE: scanning for Exposure Notification beacons (timeout: %ds)..." % t)
        scan_entries = self.scanner.scan(t)
        received_beacons = []
        for scan_entry in scan_entries:
            service = scan_entry.getValueText(ScanEntry.COMPLETE_16B_SERVICES)
            if service == "0000fd6f-0000-1000-8000-00805f9b34fb":
                data = scan_entry.getValueText(ScanEntry.SERVICE_DATA_16B)
                # service data is a hex string: 6ffd 00112233445566778899aabbccddeeff 11223344 (UUID, RPI, AEM)
                if len(data) == 44 and int(data[0:2], 16) + int(data[2:4], 16) * 0x100 == 0xfd6f:
                    rpi = bytes.fromhex(data[4:36])
                    aem = bytes.fromhex(data[36:44])
                    bdaddr = scan_entry.addr + " (" + scan_entry.addrType + ")"
                    rssi = scan_entry.rssi
                    received_beacons.append(ENBeaconRx(rpi, aem, rssi, bdaddr))
        return received_beacons
