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

    $ python3 exposure-notification.py 
    Exposure Notification BLE Simulator
    This script simulates an 'Exposure Notification V1.2'-enabled device.

    TX: TEK should roll...
    CRYPTO: Rolled TEK at i: 2648880 (hex 306b2800). New TEK: 356cb7fb1ed9afdcaeefdfa9474731cd
    CRYPTO: RPIK: 131cc76f0f1fd7853fb7e0919fac9532
    CRYPTO: AEMK: 3a2056a3fd035ef9d6d6d54a710d3615

    TX: BDADDR should roll...
    CRYPTO: padded data: 454e2d525049000000000000a76b2800 --> RPI: 67aa5eb96013169068e93fecee4d9bdf
    CRYPTO: metadata: 400c0000 --> AEM: 23369a81
    BLE TX: RPI: 67aa5eb96013169068e93fecee4d9bdf, AEM: 23369a81, BDADDR: 35f70bb24fd5
    BLE TX: Read Advertising Channel TX Power Level: 12 dBm
    BLE TX: Power is on, now starting to advertise...
    BLE TX: OK, we are advertising.
    ....
    BLE RX: Beacon was received for 8 seconds: RPI: 7c0903b1a589d5251e19cebcba563e4c, AEM: dffea144, max. RSSI: -24, BDADDR: 14:ec:df:db:4c:b4 (random)
    ..........
    
The script will create (or append to) three files:

- `tek_data.csv` contains the daily Temporary Encryption Keys (TEK) that are used for sending beacons.
- `rx_raw_data.csv` contains all the received beacons with timestamp, RSSI and the BDADDR of the sender.
- `rx_data.csv` contains preprocessed data about the received beacons, incl. their max. RSSI. 
  An entry is generated when a beacon with a specific RPI hasn't been seen anymore for 10 seconds.

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
    
    $ pip3 install -r requirements.txt
    
    $ # Give Bluetooth access to pybleno --> Python3.7 
    $ sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/python3.7
    $ # Give Bluetooth access to bluepy --> bluepy-helper 
    $ sudo setcap 'cap_net_raw,cap_net_admin+eip' /home/pi/.local/lib/python3.7/site-packages/bluepy/bluepy-helper
    
If you modify the Linux kernel, as explained [here](linux-kernel-patching.md), you can run the script 
without special options:

    $ python3 exposure-notification.py
    
Otherwise, use 

    $ python3 exposure-notification.py --toggle
 

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
