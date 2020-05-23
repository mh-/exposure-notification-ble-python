Some Thoughts on the Exposure Notification Concept
==================================================

Privacy Concerns
----------------

I like this concept a lot: Keeping anonymous data on the users' devices only, and not tracking users' locations, will
help to reach a high degree of acceptance. Of course the fact that it will be supported by the two large smart phone 
platforms will also be crucial for the success.

Starting with version 1.1, there's also no long-term key (previously called Tracing Key) stored on the device anymore, 
but only daily random keys (TEK) which are deleted after 14 days. This is optimal for privacy: Even if users were 
forced to disclose their key material, they would, as expected, only possess 14 days worth of keys.

The concept is a good compromise that allows a user to collect anonymous data, which can help to warn of a potential 
infection, while making it reasonably difficult to track the user's movements. 
It might be possible to track users (e.g. inside a building) even across ENIntervals, because one RPI disappearing 
from scans and another one appearing immediately afterwards, with no overlapping, would indicate that the two devices 
are the same with a rather high probability. This would require a lot of receivers, though. To this end, it would be 
better if all devices changed their RPI and BDADDR synchronously; but to roll out the system quickly, it has to work 
with existing BLE stacks. I'd rather have this system activated very soon through a Play Services update, than to wait 
for all device manufacturers. 

In summary, I think that this concept offers a very good trade-off regarding privacy in the current situation.

The recently published [open source reference implementation of an Exposure Notifications 
server](https://github.com/google/exposure-notifications-server) includes the use of a "device attestation API", 
such as the [SafetyNet Attestation API](https://developer.android.com/training/safetynet/attestation). 
The purpose is to validate TEKs, i.e. prevent hacked devices from reporting fake TEKs as Diagnosis Keys. 
The [SafetyNet ToS](https://developer.android.com/training/safetynet/attestation#safetynet-tos) state that this 
"works by collecting hardware and software information, such as device and application data (...), 
and sending that data to Google for analysis". I think that's fine in general, but an actual COVID-19- warning app 
should _not_ invoke this API _only_ when a user has been infected, but independently of this - so that the device data
cannot be linked to this sensitive information.

Another [concern](https://github.com/corona-warn-app/cwa-documentation/issues/76#issuecomment-629996392) would be that 
third party apps or services could use BLE scanning to do the same as an official COVID-19 warning app - even on devices
where that warning app is not installed -  and could thus make the same estimations about the user's exposure status (using 
Diagnosis Keys downloaded from official sources). Therefore it would be better if Android filtered out 0xFD6F beacons from 
"normal" BLE scanning responses, unless the user specifically allows this.

Cryptography on BLE
-------------------

I believe the cryptography concept v1.2 will properly protect the users' privacy. 

Evolved from v1.0, it still contains key derivation, although this doesn't really seem to be necessary anymore. 
There doesn't seem to be a use case where a user would be willing to release their RPI key, but not their AEM key, 
as the AEM key currently only protects the TX power, and this is absolutely required for distance estimation. 
One single AES key would be sufficient for the encryption of both ENIntervalNumber and the metadata.

I could maybe envision a setup where the TX power is instead XORed into one of the RPI byte (which still keeps the 
false-positive probability reasonably low), and use the AEM for a longer-term user identifier, which might help users to 
better understand their exposure risk. Or the AEM could be used for some other type of data, that some infected users 
might - and some others might not - be willing to disclose, and in this context key derivation could be useful. 
But this would require only one key derivation, not two.

Anyway, I believe that the overall security of the concept is strong and adequate.

Distance Measurement
--------------------

Estimating the distance from the RF signal attenuation will unfortunately not yield very precise results. 
The measured attenuation depends on the distance, but also on many other factors, e.g. the relative orientation 
of the antennas. Even with completely stationary Raspberry Pi devices, I still got large fluctuations in the RSSI 
measurements. I don't think it will be possible to distinguish between two people sitting next to each other and 
two people sitting in adjacent rooms.

The best strategy will probably be a frequent scanning, and using the maximum of the RSSI values, hoping that movement of
the devices will yield an optimal transmission at least once. However, this needs to be balanced with battery power 
consumption.

Again, this is a trade-off; even though having UWB support in all devices would make this a lot more accurate, 
I'd rather not wait for that.

-----

_Disclaimer: All views expressed are my own personal opinions. All information is provided "as is", with no guarantee of 
completeness, accuracy, timeliness or of the results obtained from the use of this information._
