#!/usr/bin/env python3
"""
- Generates ECDSA (secp256k1) private (32 bytes) and public (64 bytes) keys.
- Writes the private key in 'acsec1...' (Bech32) format and the public key in 'acpub1...' (Bech32) format to .txt files.
"""

from ecdsa import SigningKey, SECP256k1
from bech32 import bech32_encode, convertbits


def main():
    # 1) Generate ECDSA-secp256k1 private key
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.verifying_key

    # 2) Retrieve raw byte data
    private_bytes = sk.to_string()  # 32 bytes
    public_bytes = vk.to_string()   # 64 bytes (X and Y coordinates)

    # 3) Bech32 encode
    #    - convertbits(..., 8, 5): Converts 8-bit byte data to 5-bit groups
    priv_5bit = convertbits(private_bytes, 8, 5, True)
    pub_5bit = convertbits(public_bytes, 8, 5, True)

    #    - bech32_encode(hrp, data): Returns a bech32 string in the "hrp1..." format
    bech32_private = bech32_encode("acsec", priv_5bit)  # Private key = acsec1...
    bech32_public = bech32_encode("acpub", pub_5bit)    # Public key  = acpub1...

    # 4) Write to files
    with open("private_key_bech32.txt", "w") as f:
        f.write(bech32_private + "\n")

    with open("public_key_bech32.txt", "w") as f:
        f.write(bech32_public + "\n")

    print("Keys generated and saved to .txt files in Bech32 format:")
    print(f" - private_key_bech32.txt (acsec1...)")
    print(f" - public_key_bech32.txt  (acpub1...)")


if __name__ == "__main__":
    main()
