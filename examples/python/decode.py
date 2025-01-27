#!/usr/bin/env python3
"""
- User is prompted to provide:
  1) Target file path (to be created or updated)
  2) Public key (acpub1...)
  3) A single code line: ac{base64EncodedFile}{acsig1...}

- From this single code line, the base64-encoded data and the acsig signature are extracted.
- If the ECDSA-secp256k1 signature is verified, the file is created or updated.
"""

import base64
import os
import sys
import subprocess

from ecdsa import VerifyingKey, SECP256k1, BadSignatureError
from bech32 import bech32_decode, convertbits

def decode_bech32_public_key(bech32_string):
    """
    Takes a public key in 'acpub1...' bech32 format and returns the raw 64-byte key.
    
    Args:
        bech32_string (str): The bech32-encoded public key string.
    
    Returns:
        bytes: The raw 64-byte public key.
    
    Raises:
        ValueError: If the HRP is incorrect or the key length is invalid.
    """
    hrp, data = bech32_decode(bech32_string)
    if hrp != "acpub":
        raise ValueError(f"Invalid HRP for public key, expected 'acpub' but got '{hrp}'")

    decoded = convertbits(data, 5, 8, False)
    pub_bytes = bytes(decoded)
    if len(pub_bytes) != 64:
        raise ValueError(f"Invalid public key length (expected 64 bytes, got {len(pub_bytes)})")
    return pub_bytes

def decode_bech32_signature(bech32_string):
    """
    Decodes a signature in 'acsig1...' bech32 format into a raw 64-byte ECDSA signature.
    
    Args:
        bech32_string (str): The bech32-encoded signature string.
    
    Returns:
        bytes: The raw 64-byte ECDSA signature.
    
    Raises:
        ValueError: If the HRP is incorrect or the signature length is invalid.
    """
    hrp, data = bech32_decode(bech32_string)
    if hrp != "acsig":
        raise ValueError(f"Invalid HRP for signature, expected 'acsig' but got '{hrp}'")

    decoded = convertbits(data, 5, 8, False)
    sig_bytes = bytes(decoded)
    if len(sig_bytes) != 64:
        raise ValueError(f"Invalid signature length (expected 64 bytes, got {len(sig_bytes)})")
    return sig_bytes

def main():
    # 1) Prompt user for the target file path
    print("=== Apply Encode File ===")
    target_file = input("Enter the path of the file to create or update: ").strip()

    # 2) Prompt for the public key (acpub1...)
    pubkey_bech32 = input("Enter your secp256k1 public key in bech32 format (acpub1...): ").strip()
    try:
        pub_bytes = decode_bech32_public_key(pubkey_bech32)
    except Exception as e:
        print(f"Public key decoding error: {e}")
        sys.exit(1)

    # 3) Prompt for the single code line: ac{base64EncodedFile}{acsig1...}
    print("\nPaste the single code line (ac + base64 + acsig1...) and press Enter:")
    single_code_line = input().strip()

    # Check if the line starts with "ac"
    if not single_code_line.startswith("ac"):
        print("Error: The code line must start with 'ac'.")
        sys.exit(1)

    # Find the 'acsig1' segment to separate base64 data and the signature
    sig_index = single_code_line.find("acsig1", 2)  # Start searching from index 2
    if sig_index == -1:
        print("Error: The code does not contain the 'acsig1' signature part.")
        sys.exit(1)

    # Extract base64 data from after 'ac' up to before 'acsig1'
    base64_encoded = single_code_line[2:sig_index]
    signature_str = single_code_line[sig_index:]

    # 4) Decode the signature
    try:
        signature_bytes = decode_bech32_signature(signature_str)
    except Exception as e:
        print(f"Signature decoding error: {e}")
        sys.exit(1)

    # 5) Decode base64 to get the file bytes
    try:
        file_bytes = base64.b64decode(base64_encoded)
    except Exception as e:
        print(f"Base64 decoding error: {e}")
        sys.exit(1)

    # 6) Verify the signature
    vk = VerifyingKey.from_string(pub_bytes, curve=SECP256k1)
    try:
        vk.verify(signature_bytes, file_bytes)
        print("Signature verified. Creating or updating the file...")
    except BadSignatureError:
        print("Invalid signature! The file will not be created or updated.")
        sys.exit(1)

    # 7) Write the file
    try:
        with open(target_file, "wb") as f:
            f.write(file_bytes)
        print(f"File successfully created or updated: {target_file}")
    except Exception as e:
        print(f"File writing error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
