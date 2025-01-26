#!/usr/bin/env python3
"""
- Prompts the user for:
  1) Git repository directory
  2) Public key (acpub1...)
  3) A single code line: ac{base64Diff}{acsig1...}

- From this single code line, extracts the base64 diff and the `acsig` signature.
- If the ECDSA-secp256k1 signature is verified, applies the git patch.
"""

import base64
import os
import subprocess
import sys

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
    # 1) Prompt for the Git repository directory
    repo_directory = input("Enter the path to the Git repository (or folder to patch): ").strip()
    if not os.path.isdir(repo_directory):
        print(f"Error: '{repo_directory}' is not a valid directory.")
        sys.exit(1)

    # 2) Prompt for the public key (acpub1...)
    pubkey_bech32 = input("Enter your secp256k1 public key in bech32 (acpub1...): ").strip()
    try:
        pub_bytes = decode_bech32_public_key(pubkey_bech32)
    except Exception as e:
        print(f"Error decoding public key: {e}")
        sys.exit(1)

    # 3) Prompt for the single code line: ac{base64Diff}{acsig1...}
    print("\nPaste the single code line (ac + base64 + acsig1...) then press Enter:")
    single_code_line = input().strip()

    # Check if the line starts with "ac"
    if not single_code_line.startswith("ac"):
        print("Error: Code line must start with 'ac'.")
        sys.exit(1)

    # Find the 'acsig1' segment to separate base64 data and the signature
    sig_index = single_code_line.find("acsig1", 2)  # Start searching from index 2
    if sig_index == -1:
        print("Error: Could not find 'acsig1' signature portion in the code.")
        sys.exit(1)

    # Extract base64 data from after 'ac' up to before 'acsig1'
    base64_patch = single_code_line[2:sig_index]
    signature_str = single_code_line[sig_index:]

    # 4) Decode the signature
    try:
        signature_bytes = decode_bech32_signature(signature_str)
    except Exception as e:
        print(f"Error decoding signature: {e}")
        sys.exit(1)

    # 5) Decode base64 to get the diff bytes
    try:
        diff_bytes = base64.b64decode(base64_patch)
    except Exception as e:
        print(f"Error decoding Base64: {e}")
        sys.exit(1)

    # 6) Verify the signature
    vk = VerifyingKey.from_string(pub_bytes, curve=SECP256k1)
    try:
        vk.verify(signature_bytes, diff_bytes)
        print("Signature is valid. Attempting to apply patch...")
    except BadSignatureError:
        print("Invalid signature! Patch will NOT be applied.")
        sys.exit(1)

    # 7) Apply the git patch
    try:
        diff_text = diff_bytes.decode("utf-8", errors="replace")
    except UnicodeDecodeError as e:
        print(f"Error decoding diff bytes to text: {e}")
        sys.exit(1)

    result = subprocess.run(
        ["git", "apply", "--reject", "--whitespace=fix"],
        cwd=repo_directory,
        input=diff_text.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode == 0:
        print("Patch applied successfully via git apply.")
    else:
        print("Error applying patch with git apply:")
        if result.stderr:
            print(result.stderr.decode())
        if result.stdout:
            print(result.stdout.decode())


if __name__ == "__main__":
    main()
