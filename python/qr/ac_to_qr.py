#!/usr/bin/env python3
"""
- Converts the data inside 'ac.txt' to Base64 format and generates a QR code.
- Visualizes the Base64 data as a QR code and saves it.
- For long data, splits the QR codes into parts and creates a GIF.
- Install required packages with:
    pip install qrcode[pil] imageio
"""

import base64
import qrcode
import sys
import imageio
from PIL import Image

def read_ac_file(file_path):
    """
    Reads the 'ac.txt' file and returns its content.

    Args:
        file_path (str): The path to the 'ac.txt' file.

    Returns:
        str: The content of the 'ac.txt' file.

    Raises:
        SystemExit: If the file is not found or cannot be read.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            ac_string = f.read().strip()
            return ac_string
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"File reading error: {e}")
        sys.exit(1)

def ac_to_base64(ac_string):
    """
    Converts the AC string to Base64 format.

    Args:
        ac_string (str): The original AC string.

    Returns:
        str: The Base64-encoded string.

    Raises:
        SystemExit: If the conversion fails.
    """
    try:
        base64_str = base64.b64encode(ac_string.encode('utf-8')).decode('utf-8')
        return base64_str
    except Exception as e:
        print(f"Error during Base64 conversion: {e}")
        sys.exit(1)

def determine_qr_params(data_length):
    """
    Determines the QR code version, box size, and border based on data length.

    Args:
        data_length (int): The length of the data to be encoded.

    Returns:
        tuple: A tuple containing (version, box_size, border).
    """
    if data_length < 100:
        return 1, 10, 4
    elif data_length < 500:
        return 5, 8, 4
    elif data_length < 1000:
        return 10, 6, 4
    else:
        return 20, 5, 4

def generate_qr_code(data, output_file="ac_base64_qr.png"):
    """
    Generates a QR code from a Base64 string and saves it as an image.

    Args:
        data (str): The Base64-encoded data to be converted into a QR code.
        output_file (str, optional): The filename for the saved QR code image. Defaults to "ac_base64_qr.png".
    """
    version, box_size, border = determine_qr_params(len(data))
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white").convert("RGB")
    img.save(output_file)
    img.show()
    print(f"QR code saved as '{output_file}'.")

def split_and_generate_qr_gif(base64_data, chunk_size=500, gif_output="ac_base64_qr.gif"):
    """
    Splits long Base64 data into chunks, generates QR codes for each chunk, and compiles them into a GIF.

    Args:
        base64_data (str): The complete Base64-encoded data.
        chunk_size (int, optional): The maximum size of each chunk. Defaults to 500.
        gif_output (str, optional): The filename for the saved GIF. Defaults to "ac_base64_qr.gif".
    """
    frames = []
    total_parts = (len(base64_data) + chunk_size - 1) // chunk_size
    for i in range(0, len(base64_data), chunk_size):
        chunk = base64_data[i:i + chunk_size]
        version, box_size, border = determine_qr_params(len(chunk))
        # Adding a sequence label to each chunk for order tracking
        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(f"{i // chunk_size + 1}P{total_parts}QR: " + chunk)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white").convert("RGB")
        frames.append(img)
    
    # Save all frames as a GIF
    frames[0].save(gif_output, save_all=True, append_images=frames[1:], duration=100, loop=0)
    print(f"QR code GIF saved as '{gif_output}'.")

def main():
    # 1) Read the 'ac.txt' file
    ac_string = read_ac_file("ac.txt")
    print(f"Original AC: {ac_string}")

    # 2) Convert AC to Base64
    base64_encoded = ac_to_base64(ac_string)
    print(f"Base64 Encoded Data: {base64_encoded}")

    # 3) Convert data to QR code or create GIF for long data
    if len(base64_encoded) > 500:
        split_and_generate_qr_gif(base64_encoded)
    else:
        generate_qr_code(base64_encoded)

if __name__ == "__main__":
    main()
