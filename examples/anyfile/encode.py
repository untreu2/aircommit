#!/usr/bin/env python3
"""
- Prompts the user for a file path.
- Converts the file's content to base64.
- Signs the encoded data using ECDSA-secp256k1; converts the signature to bech32 format (`acsig1...`).
- Outputs a single line in the following format and saves it to `ac.txt`:
    ac{base64EncodedFile}{acsig1...}
  For example:
    acU29tZSBleGFtcGxlIGNvbnRlbnQ=acsig1qw...
"""

import base64
import sys
import os
import subprocess

from ecdsa import SigningKey, SECP256k1
from bech32 import bech32_decode, bech32_encode, convertbits

def decode_bech32_private_key(bech32_string):
    """
    Takes a private key in 'acsec1...' bech32 format and returns the raw 32-byte key.

    Args:
        bech32_string (str): The bech32-encoded private key string.

    Returns:
        bytes: The raw 32-byte private key.

    Raises:
        ValueError: If the HRP is incorrect or the key length is invalid.
    """
    hrp, data = bech32_decode(bech32_string)
    if hrp != "acsec":
        raise ValueError(f"Invalid HRP for private key, expected 'acsec' but got '{hrp}'")

    decoded = convertbits(data, 5, 8, False)
    private_bytes = bytes(decoded)
    if len(private_bytes) != 32:
        raise ValueError(f"Invalid private key length (expected 32 bytes, got {len(private_bytes)})")
    return private_bytes

def encode_signature_bech32(signature_bytes):
    """
    Converts a 64-byte signature to bech32 format ('acsig1...').

    Args:
        signature_bytes (bytes): The raw 64-byte ECDSA signature.

    Returns:
        str: The bech32-encoded signature string.
    """
    sig_5bit = convertbits(signature_bytes, 8, 5, True)
    return bech32_encode("acsig", sig_5bit)

def main():
    # 1) Prompt the user for the file path
    print("=== Fetch Encode File ===")
    file_path = input("Enter the path of the file you want to encode: ").strip()

    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a valid file.")
        sys.exit(1)

    # 2) Convert the file content to base64
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        encoded_file = base64.b64encode(file_bytes).decode("utf-8")
    except Exception as e:
        print(f"Error: Could not read or encode the file to base64: {e}")
        sys.exit(1)

    # 3) Prompt for the private key (acsec1...)
    bech32_privkey = input("Enter your secp256k1 private key in bech32 format (acsec1...): ").strip()
    try:
        private_bytes = decode_bech32_private_key(bech32_privkey)
    except Exception as e:
        print(f"Private key decoding error: {e}")
        sys.exit(1)

    # Initialize the signing key
    sk = SigningKey.from_string(private_bytes, curve=SECP256k1)

    # 4) Create the signature (64 bytes)
    signature_bytes = sk.sign(file_bytes)
    sig_bech32 = encode_signature_bech32(signature_bytes)

    # 5) Create the single code output: ac{encoded_file}{sig_bech32}
    single_code = f"ac{encoded_file}{sig_bech32}"

    # 6) Save to ac.txt file
    output_file = "ac.txt"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"```\n{single_code}\n```")
        print(f"\n--- SINGLE CODE OUTPUT ---")
        print(f"{single_code}")
        print("--------------------------\n")
        print(f"Single code line successfully saved to '{output_file}'.")
    except Exception as e:
        print(f"Error: Could not save the single code line to '{output_file}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
