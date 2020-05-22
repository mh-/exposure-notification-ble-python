exposure-notification-ble-python
================================

Exposure Notification BLE Simulator
-----------------------------------

This is a Python implementation of the __COVID-19 "Exposure Notification"__ (previously "Contact Tracing") 
specifications at <https://www.google.com/covid19/exposurenotifications/>.

The `exposure-notification.py` script transmits Bluetooth Low Energy (BLE) beacons, 
and at the same time scans for them and records their contents and signal strength (RSSI).

The purpose of this is research, particularly regarding the security & privacy implications 
of this contact tracing concept, while the actual implementations on smart phones are not yet (publicly) available.

I wrote down a few thoughts about the concept [here](some_thoughts_on_the_en_concept.md).

Usage Example
-------------

    $ python3 exposure-notification.py -c 10 -s 2
    Exposure Notification BLE Simulator
    This script simulates an 'Exposure Notification V1.2'-enabled device.
    
    Full cycle duration: 10s, thereof scanning duration: 2s
    
    TX: TEK should roll...
    CRYPTO: Rolled TEK at i: 2649312 (hex e06c2800). New TEK: 7921b817fdb92074df5345594273756f
    CRYPTO: RPIK: eae8956644770f952871daf549c0ce7e
    CRYPTO: AEMK: a1d0bd6f94b053cf622ca88194e20611
    
    TX: BDADDR should roll...
    CRYPTO: padded data: 454e2d5250490000000000005b6d2800 --> RPI: 5811408cf8d88d2b33f73773a7c6d45f
    CRYPTO: metadata: 400c0000 --> AEM: a3e9517f
    BLE TX: RPI: 5811408cf8d88d2b33f73773a7c6d45f, AEM: a3e9517f, BDADDR: 3e9a0a0c3d4b
    BLE TX: Read Advertising Channel TX Power Level: 12 dBm
    BLE TX: Power is on, now starting to advertise...
    BLE TX: OK, we are advertising.
    ........
    BLE RX: Now scanning...
    ........
    BLE RX: Now scanning...
    ........
    BLE RX: Now scanning...
    ........
    BLE RX: Now scanning...
    ........
    BLE RX: Now scanning...
    ........
    BLE RX: Now scanning...
    
    BLE RX: Beacon was received for 20 seconds: RPI: 8c3f2c091ad2f7c5da409a3171b96f6f, AEM: 11c15a1b, max. RSSI: -44, BDADDR: 0c:33:79:93:2c:1a (random)
    ....
    
The script will create (or append to) these files:

- `tek_data.csv` contains the daily Temporary Encryption Keys (TEK) that are used for sending beacons.
- `rx_raw_data.csv` contains all the received beacons with timestamp, RSSI and the BDADDR of the sender. 
(Only with option `-r` / `--storerawdata`.)
- `rx_data.csv` contains preprocessed data about the received beacons, incl. their max. RSSI. 
  An entry is generated when a beacon with a specific RPI hasn't been seen anymore for a certain time, which depends 
  on the selected cycle time.

Hardware Requirements
---------------------

This package has been developed for the __Raspberry Pi__ platform, and has been tested on 
Raspberry Pi 3B+ and Raspberry Pi Zero W, using their integrated BLE hardware.

Software Requirements
---------------------

- __Linux__ incl. __bluez__ 
(tested with [Raspbian Buster Lite](https://www.raspberrypi.org/downloads/raspbian/), Version Feb. 2020)
- __Python 3__ (tested with Python 3.7.3, which is included in the Raspbian package)
- [__bluepy__](https://github.com/IanHarvey/bluepy) by Ian Harvey, used for scanning for beacons (BLE RX)
- [__pybleno__](https://github.com/Adam-Langley/pybleno) by Adam Langley, used for sending beacons (BLE TX) - 
I created a [__fork__](https://github.com/mh-/pybleno/tree/enhancements-for-exposure-notification) with a few 
[small enhancements](https://github.com/Adam-Langley/pybleno/compare/master...mh-:enhancements-for-exposure-notification) 
to exactly mimic the Exposure Notification specification.
- Because the out-of-the-box Raspberry Pi Linux bluez stack (kernel 4.19.97+) stops sending BLE beacons during BLE 
scanning, which is somewhat sub-optimal for the use case and probably not the behavior of real smart phones, I created a
[__kernel patch__](linux-kernel-patching.md). (Actually it's a dirty hack which has been only tested in this one 
scenario - kernel 5.7 will probably solve this in a better way, but isn't tested on the Raspberry Pi platform yet). 
If you prefer to keep your existing kernel, the script can also simply toggle between transmit-only and scan-only phases.

Installation and Running the Script
-----------------------------------

    $ git clone https://github.com/mh-/exposure-notification-ble-python
    $ cd exposure-notification-ble-python
    
    $ # Install GPS support, incl. Python library
    $ sudo apt install gpsd gpsd-clients

    $ pip3 install -r requirements.txt
    
    $ # Give Bluetooth access to pybleno --> Python3.7 
    $ sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/python3.7
    $ # Give Bluetooth access to bluepy --> bluepy-helper 
    $ sudo setcap 'cap_net_raw,cap_net_admin+eip' /home/pi/.local/lib/python3.7/site-packages/bluepy/bluepy-helper
        
If you modify the Linux kernel, as explained [here](linux-kernel-patching.md), you can run the script 
without special options:

    $ python3 exposure-notification.py
    
With the original Linux kernel, advertising the beacon (TX) is disabled by scanning (RX), 
and you need use the --triggertx option:

    $ python3 exposure-notification.py --triggertx
    
You can set the duration of a cycle, and the duration of scanning within a cycle, with these options:

      -c CYCLETIME, --cycletime CYCLETIME
                            duration (in seconds) of one cycle
      -s SCANTIME, --scantime SCANTIME
                            duration (in seconds) of the scanning within one cycle
 
If you do not specify options, the script will use these durations:

    $ python3 exposure-notification.py -c 300 -s 2

The script will always scan in steps of 2 seconds.

You can choose to have a raw RX data file created (`rx_raw_data.csv`) with option `-r` / `--storerawdata`:

    $ python3 exposure-notification.py --storerawdata
    
If you have a GPS connected to the Raspberry Pi which is supported by gpsd, you can use these option:

      -d, --gpsdatetime     set date and time from GPS
      -g, --gpsposition     store GPS position with RX data

Running the Script at Startup
-----------------------------

If you want to run the script every time the Raspberry Pi starts up, you can e.g. make __systemd__ run the script
when the boot sequence has finished (and Bluetooth has been activated).

There's a sample Service Unit file in this repo: `exposure-notification.service`. Modify this with the command line
parameters you need and then: 

    $ sudo cp exposure-notification.service /lib/systemd/system/
    $ sudo chmod 644 /lib/systemd/system/exposure-notification.service
    $ sudo systemctl daemon-reload
    $ sudo systemctl enable exposure-notification.service
    $ sudo reboot
    
Read the log with
    
    $ journalctl -e -u exposure-notification.service 

Limitations
-----------
Our own TX power level is read, but only printed, not used for setting the AEM value. That's not a big deal, 
because the value that can be read is always the same (+12 dBm on Raspberry Pi 3B+ and Zero W - which is strange 
because the Bluetooth spec lists a maximum of 10dBm). 
I initially planned to read and use this value, but then had to split the `ENTxService` object so that a 
separate script starts the TX beacon, `pybleno` stops at the end of this script, and we can do `sudo hciconfig hci0 down; 
sudo hciconfig hci0 up` when the BLE stack temporarily stops working.

-----

_Disclaimer: All views expressed are my own personal opinions. All information is provided "as is", with no guarantee of 
completeness, accuracy, timeliness or of the results obtained from the use of this information._
