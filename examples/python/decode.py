#!/usr/bin/env python3
"""
This script decodes the `ac` formatted code from the `ac.txt` file:
- It reads the code in the format `ac{base64EncodedFile}{acsig1...}`.
- Decodes the Base64-encoded file content to retrieve the original file.
- Decodes the Bech32-encoded signature.
- Optionally verifies the signature's validity.
"""

import base64
import sys
import os

from ecdsa import VerifyingKey, SECP256k1, BadSignatureError
from bech32 import bech32_decode, convertbits

def decode_bech32_signature(bech32_string):
    """
    Decodes a Bech32-formatted signature ('acsig1...').

    Args:
        bech32_string (str): The Bech32-encoded signature.

    Returns:
        bytes: The raw signature bytes.
    
    Raises:
        ValueError: If the signature format is invalid.
    """
    hrp, data = bech32_decode(bech32_string)
    if hrp != "acsig":
        raise ValueError(f"Invalid HRP for signature, expected 'acsig' but got '{hrp}'.")
    
    decoded = convertbits(data, 5, 8, False)
    if decoded is None:
        raise ValueError("Error during Bech32 conversion.")
    signature_bytes = bytes(decoded)
    if len(signature_bytes) != 64:
        raise ValueError(f"Invalid signature length (expected 64 bytes, got {len(signature_bytes)}).")
    return signature_bytes

def decode_bech32_private_key(bech32_string):
    """
    Decodes a Bech32-formatted private key ('acsec1...').

    Args:
        bech32_string (str): The Bech32-encoded private key.

    Returns:
        bytes: The raw 32-byte private key.
    
    Raises:
        ValueError: If the private key format is invalid.
    """
    hrp, data = bech32_decode(bech32_string)
    if hrp != "acsec":
        raise ValueError(f"Invalid HRP for private key, expected 'acsec' but got '{hrp}'.")
    
    decoded = convertbits(data, 5, 8, False)
    if decoded is None:
        raise ValueError("Error during Bech32 conversion.")
    private_bytes = bytes(decoded)
    if len(private_bytes) != 32:
        raise ValueError(f"Invalid private key length (expected 32 bytes, got {len(private_bytes)}).")
    return private_bytes

def decode_bech32_public_key(bech32_string):
    """
    Decodes a Bech32-formatted public key ('acpub1...').

    Args:
        bech32_string (str): The Bech32-encoded public key.

    Returns:
        bytes: The raw public key bytes.
    
    Raises:
        ValueError: If the public key format is invalid.
    """
    hrp, data = bech32_decode(bech32_string)
    if hrp != "acpub":
        raise ValueError(f"Invalid HRP for public key, expected 'acpub' but got '{hrp}'.")
    
    decoded = convertbits(data, 5, 8, False)
    if decoded is None:
        raise ValueError("Error during Bech32 conversion.")
    pubkey_bytes = bytes(decoded)
    if len(pubkey_bytes) not in (64):
        raise ValueError(f"Invalid public key length (expected 64 bytes, got {len(pubkey_bytes)}).")
    return pubkey_bytes

def main():
    print("=== AC Code Decoder ===")

    # 1. Check for the ac.txt file
    input_file = "ac.txt"
    if not os.path.isfile(input_file):
        print(f"Error: '{input_file}' file not found.")
        sys.exit(1)

    # 2. Read the ac.txt file
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            ac_code = f.read().strip()
    except Exception as e:
        print(f"Error: Unable to read '{input_file}' file: {e}")
        sys.exit(1)

    # Verify that the code starts with 'ac'
    if not ac_code.startswith("ac"):
        print("Error: Code does not start with 'ac'.")
        sys.exit(1)

    # Find and separate the 'acsig1' substring
    sig_start = ac_code.find("acsig1")
    if sig_start == -1:
        print("Error: 'acsig1' signature not found in the code.")
        sys.exit(1)

    base64_part = ac_code[2:sig_start]
    sig_part = ac_code[sig_start:]

    # 3. Decode the Base64 content
    try:
        file_bytes = base64.b64decode(base64_part)
    except Exception as e:
        print(f"Error: Unable to decode Base64 content: {e}")
        sys.exit(1)

    # 4. Decode the signature part
    try:
        signature_bytes = decode_bech32_signature(sig_part)
    except Exception as e:
        print(f"Error: Issue decoding signature: {e}")
        sys.exit(1)

    # 5. Save the decoded file
    output_file = "decoded_file"
    try:
        with open(output_file, "wb") as f:
            f.write(file_bytes)
        print(f"File successfully saved as '{output_file}'.")
    except Exception as e:
        print(f"Error: Unable to save the file: {e}")
        sys.exit(1)

    # 6. Optional: Verify the signature
    verify = input("Do you want to verify the signature? (y/n): ").strip().lower()
    if verify == 'y':
        # Prompt the user to enter their public key
        pubkey_bech32 = input("Enter your public key in Bech32 format (acpub1...): ").strip()
        try:
            pubkey_bytes = decode_bech32_public_key(pubkey_bech32)
        except Exception as e:
            print(f"Public key decoding error: {e}")
            sys.exit(1)
        
        try:
            vk = VerifyingKey.from_string(pubkey_bytes, curve=SECP256k1)
        except Exception as e:
            print(f"Error loading public key: {e}")
            sys.exit(1)
        
        # Verify the signature
        try:
            vk.verify(signature_bytes, file_bytes)
            print("Signature verification: Valid.")
        except BadSignatureError:
            print("Signature verification: Invalid!")
        except Exception as e:
            print(f"Error during signature verification: {e}")
    else:
        print("Signature verification skipped.")

if __name__ == "__main__":
    main()
