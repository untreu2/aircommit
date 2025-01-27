import hashlib
import bip39

def read_ac_file(file_path):
    """Reads the 'ac.txt' file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            ac_string = f.read().strip()
            return ac_string
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found.")
        exit(1)
    except Exception as e:
        print(f"File reading error: {e}")
        exit(1)

def string_to_mnemonic(input_string):
    """Hashes the AC string with SHA-256 and generates a BIP-39 mnemonic."""
    # Hash the input string using SHA-256
    hashed_bytes = hashlib.sha256(input_string.encode()).digest()
    
    # Generate mnemonic words in BIP-39 format from the hashed bytes
    mnemonic = bip39.encode_bytes(hashed_bytes)
    
    return mnemonic

def main():
    # 1) Read the AC file
    ac_string = read_ac_file("ac.txt")
    print(f"Read AC Content: {ac_string}")

    # 2) Generate Mnemonic
    mnemonic_words = string_to_mnemonic(ac_string)
    print("\nGenerated Mnemonic Words:")
    print(mnemonic_words)

if __name__ == "__main__":
    main()
