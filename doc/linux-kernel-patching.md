Linux Kernel Patching
=====================

### Why should you modify the kernel?

Bluez, the Linux Bluetooth stack, switches LE Advertising off while scanning for advertisements from other devices.
This can be observed with `sudo btmon`:
```
@ MGMT Open: bluepy-helper (privileged) version 1.14                                                                                 {0x0003} 7.786839
@ MGMT Command: Read Management Version Information (0x0001) plen 0                                                                  {0x0003} 7.787706
@ MGMT Event: Command Complete (0x0001) plen 6                                                                                       {0x0003} 7.787725
      Read Management Version Information (0x0001) plen 3
        Status: Success (0x00)
        Version: 1.14
@ MGMT Command: Start Discovery (0x0023) plen 1                                                                               {0x0003} [hci0] 7.788614
        Address type: 0x06
          LE Public
          LE Random
< HCI Command: LE Set Advertise Enable (0x08|0x000a) plen 1                                                                       #121 [hci0] 7.788724
        Advertising: Disabled (0x00)
> HCI Event: Command Complete (0x0e) plen 4                                                                                       #122 [hci0] 7.789750
      LE Set Advertise Enable (0x08|0x000a) ncmd 1
        Status: Success (0x00)
```
The first HCI command the `@ MGMT Command: Start Discovery` sends is 
`LE Set Advertise Enable` with `Advertising: Disabled`.

Many BLE chips can however interleave advertising and scanning with a high frequency, so that the probability that two 
devices "see" each other during the process is much higher. Therefore I wanted to try to keep advertising on all the time.

The responsible code is not part of the bluez user space package, but in the kernel space in 
`net/bluetooth/hci_request.c`, `active_scan()`. You can view the kernel code e.g. here:
https://elixir.bootlin.com/linux/v4.19.97/source/net/bluetooth/hci_request.c

The problem is caused here - `__hci_req_disable_advertising()` sends the HCI Request "Disable Advertising":
```
static int active_scan(struct hci_request *req, unsigned long opt)
{
	uint16_t interval = opt;
	struct hci_dev *hdev = req->hdev;
	u8 own_addr_type;
	int err;

	BT_DBG("%s", hdev->name);

	if (hci_dev_test_flag(hdev, HCI_LE_ADV)) {
		hci_dev_lock(hdev);

		/* Don't let discovery abort an outgoing connection attempt
		 * that's using directed advertising.
		 */
		if (hci_lookup_le_connect(hdev)) {
			hci_dev_unlock(hdev);
			return -EBUSY;
		}

		cancel_adv_timeout(hdev);
		hci_dev_unlock(hdev);

		__hci_req_disable_advertising(req);
	}
    (...)
```
A quick&dirty hack is to simply disable that section, e.g. by replacing `if (hci_dev_test_flag(hdev, HCI_LE_ADV))` by 
`if (false)`.

Another option would be to wait for [kernel version 5.7](https://elixir.bootlin.com/linux/v5.7-rc5/source/net/bluetooth/hci_request.c)
where this is handled differently, and where parallel advertising and scanning will probably work. 
But this isn't part of the [Raspberry Pi kernel source tree](https://github.com/raspberrypi/linux) yet.

### How to modify the kernel?

If you feel comfortable applying this hack to a Raspberry Pi setup, here's what you have to do:

1. Read the tutorial at https://www.raspberrypi.org/documentation/linux/kernel/building.md
2. On your Raspberry Pi, do `uname -r`.  
For Raspbian Buster, this shows the kernel version `4.19.97-v7+`.  
The corresponding git repo is located here <https://github.com/raspberrypi/linux/tree/rpi-4.19.y>, you can clone it with
`git clone --depth=1 --branch rpi-4.19.y https://github.com/raspberrypi/linux`
2. __Apply the [patch](../linux-ble-patch/keep_ble_advertising_on_when_scanning.patch):__  
`patch -p0 < keep_ble_advertising_on_when_scanning.patch`
3. Build the kernel as explained in the tutorial. This will take some time.
4. Deploy the kernel to the Raspberry Pi's SD card.


-----

_Disclaimer: All views expressed are my own personal opinions. All information is provided "as is", with no guarantee of 
completeness, accuracy, timeliness or of the results obtained from the use of this information._
