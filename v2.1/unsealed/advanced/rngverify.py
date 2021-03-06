#!/usr/bin/env python
from __future__ import print_function
from binascii import a2b_hex

ADDRESS         = '1KcJazDdetcENpjsouWSNj2QQpsryAYERk   '.strip()
PRIVKEY         = '5KML3zBUnMsdYjwXqzzDPPSZm5tP2ToryDyxkkN8aNRnre2vL5i'.strip()
OD_NONCE        = a2b_hex('da9559ded92b02c56428c816b1c6ba15e61ee400eaa20122f937e34097e5a117')
SECRET_EXPONENT = a2b_hex('ca2e9f22257462ce00e7cdd3c853b8bb14cec5ff776b11f4046ab7ae5de6553a')
CHIP_SERIAL     = b'SPX6ESSUJVGVCIBAEBDTMDAK74'

# The above numbers can be used to prove we picked the private key using
# an algorithm that included the entropy values you provided, and therefore
# does not allow us any access to the funds. This program checks our math.
#
# Usage:
#   python rngverify.py keepme.bin
#
# Example (simplified, MacOS X):
#
#   dd if=/dev/urandom bs=256k count=1 > ~/keepme.bin
#   diskutil info /Volumes/OPENDIME/ | grep /dev/disk
#   ==> replace /dev/diskXXX in next line -- be VERY careful!! <==
#   sudo dd if=~/keepme.bin of=/dev/diskXXX
#   (.. device will self-eject ..)
#   (.. time passes, then unseal opendime ..)
#   python /Volumes/OPENDIME/advanced/rngverify.py ~/keepme.bin
#
#
import os, sys
from hashlib import sha256

SIZE = 256*1024

try:
    assert len(sys.argv) >= 2, "entropy data filename required"
    data = open(sys.argv[-1], 'rb').read(SIZE)
    assert len(data) == SIZE, "too short"
except:
    print("Need 256k bytes of data originally written during setup.\n")
    raise

# Secret exponent will be the double-SHA256 hash of:
#
#   1) customer data  (256k bytes)
#   2) usb serial number of unit (base32 encoding of 128-bit number: 26 chars)
#   3) a random number picked by device (device nonce: 256 bits)
#
should_be = sha256(sha256(data + CHIP_SERIAL + OD_NONCE).digest()).digest() 

if should_be != SECRET_EXPONENT:
    print("\nFAILED: You probably didn't record exactly the bytes written to this drive.")
    raise SystemExit

print("STEP1: Secret exponent is hash of things we expected (good).")

# Optional: verify the secret exponent is the basis of the private key
try:
    import pycoin
    from pycoin.key import Key
except:
    print("\nNeed pycoin installed for complete check:   pip install 'pycoin>=0.76'\n")
    raise SystemExit

# pull out secret key from provided secret key
k = Key.from_text(PRIVKEY)
expect = pycoin.encoding.to_bytes_32(k.secret_exponent())

if expect == should_be and k.address() == ADDRESS:
    print("\nSUCCESS: Private key uses secret exponent we expected. Perfect.")
else:
    print("\nFAILED: Something went wrong along the way. Is this the right private key?")


# EOF
