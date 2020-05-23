from Crypto.Protocol.KDF import HKDF
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import struct, time
from lib.logger import *
log = Logger()


class ENCrypto:

    def __init__(self, interval_length_minutes=10, tek_rolling_period=144):
        self.tek = bytes([0] * 16)
        self.tek_roll_interval_i = 0
        self.rpik = bytes([0] * 16)
        self.aemk = bytes([0] * 16)
        self.rpi = bytes([0] * 16)
        self.aem = bytes([0] * 16)
        self.interval_length_minutes = interval_length_minutes
        self.tek_rolling_period = tek_rolling_period

    @staticmethod
    def get_current_unix_epoch_time_seconds():
        return int(time.time())

    def en_interval_number(self, timestamp_seconds):
        return timestamp_seconds // (60 * self.interval_length_minutes)

    def get_encoded_current_en_interval_number(self):
        return struct.pack("<I", self.en_interval_number(self.get_current_unix_epoch_time_seconds()))

    def tek_should_roll(self):
        current_roll_interval = (self.en_interval_number(self.get_current_unix_epoch_time_seconds())
                                 // self.tek_rolling_period) * self.tek_rolling_period
        return current_roll_interval > self.tek_roll_interval_i

    def roll_tek(self):
        self.tek_roll_interval_i = (self.en_interval_number(self.get_current_unix_epoch_time_seconds())
                                    // self.tek_rolling_period) * self.tek_rolling_period
        self.tek = get_random_bytes(16)
        log.log("CRYPTO: Rolled TEK at i: %d (hex %s). New TEK: %s" %
                (self.tek_roll_interval_i, struct.pack("<I", self.tek_roll_interval_i).hex(), self.tek.hex()))

    def derive_keys(self):
        self.rpik = HKDF(master=self.tek, key_len=16, salt=None, hashmod=SHA256, context="EN-RPIK".encode("UTF-8"))
        log.log("CRYPTO: RPIK: %s" % self.rpik.hex())
        self.aemk = HKDF(master=self.tek, key_len=16, salt=None, hashmod=SHA256, context="EN-AEMK".encode("UTF-8"))
        log.log("CRYPTO: AEMK: %s" % self.aemk.hex())

    def encrypt_rpi(self):
        enin = self.get_encoded_current_en_interval_number()
        padded_data = "EN-RPI".encode("UTF-8") + bytes([0x00] * 6) + enin
        cipher = AES.new(self.rpik, AES.MODE_ECB)
        self.rpi = cipher.encrypt(padded_data)
        log.log("CRYPTO: padded data: %s --> RPI: %s" % (padded_data.hex(), self.rpi.hex()))

    def encrypt_aem(self, metadata, rpi):
        cipher = AES.new(self.aemk, AES.MODE_CTR, nonce=bytes(0), initial_value=rpi)
        self.aem = cipher.encrypt(bytes(metadata))
        log.log("CRYPTO: metadata: %s --> AEM: %s" % (bytes(metadata).hex(), self.aem.hex()))
