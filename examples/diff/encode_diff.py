#!/usr/bin/env python3
"""
- Detects the HEAD commit (old commit) from the local Git repository and retrieves the owner/repo information from the 'origin' remote.
- Prompts the user for a new commit URL and downloads the diff from GitHub.
- Encodes the downloaded diff into base64.
- Signs the encoded diff using ECDSA-secp256k1; converts the signature to bech32 format (`acsig1...`).
- Outputs a single line in the following format:
    ac{base64Diff}{acsig1...}
  For example:
    acMTIzNDU2Nzg5L2Jhc2U2NA==acsig1qw...
"""

import requests
import base64
import re
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


def parse_github_owner_repo(remote_url):
    """
    Extracts the owner/repo information from a Git remote URL.
    Supports 'git@github.com:...' and 'https://github.com/...' formats only.

    Args:
        remote_url (str): The Git remote URL.

    Returns:
        tuple: A tuple containing (owner, repo).

    Raises:
        ValueError: If the remote URL format is unsupported or cannot be parsed.
    """
    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]

    if remote_url.startswith("git@github.com:"):
        part = remote_url.split("git@github.com:")[-1]  # OWNER/REPO
    elif remote_url.startswith("https://github.com/"):
        part = remote_url.split("https://github.com/")[-1]
    else:
        raise ValueError(f"Unsupported or non-GitHub remote URL: {remote_url}")

    segments = part.split("/")
    if len(segments) < 2:
        raise ValueError(f"Cannot parse owner/repo from remote: {remote_url}")
    owner = segments[0]
    repo = segments[1]
    return owner, repo


def fetch_diff(old_commit_url, new_commit_url, token=None):
    """
    Returns the diff (text) between old_commit_url and new_commit_url.
    Example:
        https://github.com/OWNER/REPO/commit/SHA

    Args:
        old_commit_url (str): URL of the old commit.
        new_commit_url (str): URL of the new commit.
        token (str, optional): GitHub API token for authenticated requests.

    Returns:
        str: The diff text if successful, None otherwise.
    """
    def extract_repo_info(commit_url):
        pattern = re.compile(r"https://github\.com/([^/]+)/([^/]+)/commit/([a-f0-9]+)")
        m = pattern.match(commit_url)
        if m:
            return m.groups()
        return None, None, None

    old_owner, old_repo, old_sha = extract_repo_info(old_commit_url)
    new_owner, new_repo, new_sha = extract_repo_info(new_commit_url)

    if None in [old_owner, old_repo, old_sha, new_owner, new_repo, new_sha]:
        print("Error: Invalid commit URL format.")
        return None

    if old_owner != new_owner or old_repo != new_repo:
        print("Error: The commits belong to different repositories!")
        return None

    diff_url = f"https://github.com/{old_owner}/{old_repo}/compare/{old_sha}...{new_sha}.diff"
    headers = {}
    if token:
        # GitHub API token (optional)
        headers["Authorization"] = f"token {token}"

    try:
        r = requests.get(diff_url, headers=headers)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"Error fetching commit diff: {e}")
        return None


def main():
    # 1) Prompt for the local repository
    repo_directory = input("Enter your local Git repository path: ").strip()
    if not os.path.isdir(repo_directory):
        print(f"Error: '{repo_directory}' is not a valid directory.")
        sys.exit(1)

    if not os.path.isdir(os.path.join(repo_directory, ".git")):
        print("Error: The specified path doesn't appear to be a Git repository.")
        sys.exit(1)

    # 2) Get the local HEAD commit SHA
    try:
        old_sha = subprocess.check_output(
            ["git", "-C", repo_directory, "rev-parse", "HEAD"],
            stderr=subprocess.STDOUT
        ).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        print("Error: Could not retrieve HEAD commit SHA.")
        sys.exit(1)

    # 3) Get the 'origin' remote URL
    try:
        remote_url = subprocess.check_output(
            ["git", "-C", repo_directory, "remote", "get-url", "origin"],
            stderr=subprocess.STDOUT
        ).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        print("Error: Could not find 'origin' remote.")
        sys.exit(1)

    # Parse owner and repo from remote URL
    try:
        owner, repo = parse_github_owner_repo(remote_url)
    except ValueError as e:
        print(f"Error parsing remote URL: {e}")
        sys.exit(1)

    old_commit_url = f"https://github.com/{owner}/{repo}/commit/{old_sha}"
    print(f"Auto-detected old commit URL: {old_commit_url}")

    # 4) Prompt for the new commit URL
    new_commit_url = input("Enter the new commit URL (e.g., https://github.com/owner/repo/commit/sha): ").strip()

    # 5) (Optional) Prompt for GitHub token
    token = input("Enter your GitHub token (leave empty if not available): ").strip() or None

    # 6) Fetch the diff between old and new commits
    diff_text = fetch_diff(old_commit_url, new_commit_url, token)
    if diff_text is None:
        print("No diff data retrieved or an error occurred.")
        sys.exit(1)

    # (Optional) Save the diff to a file
    patch_path = os.path.join(repo_directory, "fetched_diff.patch")
    try:
        with open(patch_path, "w", encoding="utf-8") as f:
            f.write(diff_text)
        print(f"Diff saved to: {patch_path}")
    except Exception as e:
        print(f"Warning: Could not save diff file: {e}")

    # 7) Prompt for the private key (acsec1...)
    bech32_privkey = input("Enter your secp256k1 private key in bech32 (acsec1...): ").strip()
    try:
        private_bytes = decode_bech32_private_key(bech32_privkey)
    except Exception as e:
        print(f"Error decoding private key: {e}")
        sys.exit(1)

    sk = SigningKey.from_string(private_bytes, curve=SECP256k1)

    # 8) Encode the diff to base64
    encoded_diff = base64.b64encode(diff_text.encode("utf-8")).decode("utf-8")

    # 9) Create the signature (64 bytes)
    signature_bytes = sk.sign(diff_text.encode("utf-8"))
    sig_bech32 = encode_signature_bech32(signature_bytes)

    # 10) Generate the single code output: ac{encoded_diff}{sig_bech32}
    single_code = f"ac{encoded_diff}{sig_bech32}"

    print("\n--- SINGLE CODE OUTPUT ---")
    print(single_code)
    print("--------------------------\n")


if __name__ == "__main__":
    main()
