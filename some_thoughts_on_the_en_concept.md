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

In summary, I think that this concept offers the best possible trade-off regarding privacy in the current situation.

Cryptography
------------

I believe the cryptography v1.2 will properly protect the users' privacy. 

Evolved from v1.0, it still contains key derivation, although this doesn't really seem to be necessary anymore. 
There doesn't seem to be a use case where a user would be willing to release their RPI key, but not their AEM key, 
as the AEM key currently only protects the TX power, and this is absolutely required for distance estimation. 
One single AES key would be sufficient for the encryption of both ENIntervalNumber and the metadata.

I could maybe envision a setup where the TX power is instead XORed into one of the RPI byte (which still keeps the 
false-positive probability reasonably low), and use the AEM for a longer-term user identifier. This might help users to 
better understand their exposure risk, but some infected users might not be willing to disclose that identifier, 
and in this context key derivation could be useful. But this would require only one key derivation, not two.

Anyway, I believe that the overall security of the concept is strong and adequate.

Distance Measurement
--------------------

Estimating the distance from the RF signal attenuation will unfortunately not yield very precise results. 
The measured attenuation depends on the distance, but also on many other factors, e.g. the relative orientation 
of the antennas. Even with completely stationary Raspberry Pi devices, I still got large fluctuations in the RSSI 
measurements. I don't think it will be possible to distinguish between two people sitting next to each other and 
two people sitting in adjacent rooms.

The best strategy will probably be a frequent scanning, and using the maximum of the RSSI values, hoping that movement of
the devices will yield an optimal transmission at least once.

Again, this is a trade-off; even though having UWB support in all devices would make this a lot more accurate, 
I'd rather not wait for that.

-----

_Disclaimer: All views expressed are my own personal opinions. All information is provided "as is", with no guarantee of 
completeness, accuracy, timeliness or of the results obtained from the use of this information._
