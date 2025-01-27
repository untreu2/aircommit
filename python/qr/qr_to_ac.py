#!/usr/bin/env python3
"""
- Reads QR code images (PNG or GIF) to extract Base64-encoded data using OpenCV.
- Decodes the Base64 data to retrieve the original AC code.
- Writes the AC code to 'ac.txt'.
- Supports both single QR codes and multi-part QR codes within animated GIFs.
- Install required packages with:
    pip install opencv-python Pillow numpy
"""

import cv2
import numpy as np
import sys
import os
from PIL import Image, ImageSequence
import base64

def read_qr_image_opencv(file_path):
    """
    Reads QR codes from the provided image file using OpenCV and extracts the embedded data.

    Args:
        file_path (str): Path to the QR code image file.

    Returns:
        list of str: A list containing data extracted from each QR code found.

    Raises:
        SystemExit: If the file is not found, cannot be opened, or no QR codes are detected.
    """
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    try:
        img = Image.open(file_path)
    except Exception as e:
        print(f"Error opening image '{file_path}': {e}")
        sys.exit(1)
    
    data_list = []
    qr_detector = cv2.QRCodeDetector()

    if img.format == 'GIF':
        # Iterate through each frame in the GIF
        for frame_number, frame in enumerate(ImageSequence.Iterator(img), start=1):
            # Convert PIL image to OpenCV image
            frame_cv = cv2.cvtColor(np.array(frame.convert('RGB')), cv2.COLOR_RGB2BGR)
            data, points, _ = qr_detector.detectAndDecode(frame_cv)
            if data:
                data_list.append(data)
                print(f"Frame {frame_number}: QR Code detected and decoded.")
            else:
                print(f"Frame {frame_number}: No QR Code detected.")
    else:
        # Single-frame image (e.g., PNG)
        frame_cv = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
        data, points, _ = qr_detector.detectAndDecode(frame_cv)
        if data:
            data_list.append(data)
            print("QR Code detected and decoded.")
        else:
            print("No QR Code detected.")

    if not data_list:
        print("No QR codes found or could not be decoded.")
        sys.exit(1)

    return data_list

def reconstruct_base64(data_list):
    """
    Reconstructs the complete Base64 string from the list of decoded QR code data.

    Args:
        data_list (list of str): Data extracted from each QR code.

    Returns:
        str: The complete Base64-encoded string.

    Raises:
        SystemExit: If data format is incorrect or parts are missing.
    """
    if len(data_list) == 1:
        # Single QR code containing the entire Base64 string
        return data_list[0]
    else:
        # Multiple QR codes, each containing a part of the Base64 string with sequencing info
        parts = {}
        total_parts = None
        for data in data_list:
            try:
                # Expected format: "1P3QR: base64data"
                label, b64data = data.split("QR: ", 1)
                part_num, total = label.split("P")
                part_num = int(part_num)
                total = int(total)
                parts[part_num] = b64data
                total_parts = total
            except ValueError:
                print("Unexpected data format. Please ensure multi-part QR codes follow the 'XPYQR: data' format.")
                sys.exit(1)

        if total_parts is None or len(parts) != total_parts:
            print("Missing QR code parts. Ensure all parts are present and correctly sequenced.")
            sys.exit(1)

        # Concatenate parts in order
        base64_str = ''.join(parts[i] for i in range(1, total_parts + 1))
        return base64_str

def base64_to_ac(base64_str):
    """
    Decodes the Base64 string to retrieve the original AC code.

    Args:
        base64_str (str): The Base64-encoded string.

    Returns:
        str: The original AC code.

    Raises:
        SystemExit: If Base64 decoding fails.
    """
    try:
        ac_bytes = base64.b64decode(base64_str)
        ac_string = ac_bytes.decode('utf-8')
        return ac_string
    except Exception as e:
        print(f"Error decoding Base64 data: {e}")
        sys.exit(1)

def write_ac_file(ac_string, file_path="ac.txt"):
    """
    Writes the AC string to the specified file.

    Args:
        ac_string (str): The AC code to write.
        file_path (str, optional): Destination file path. Defaults to "ac.txt".

    Raises:
        SystemExit: If writing to the file fails.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ac_string)
        print(f"AC code successfully written to '{file_path}'.")
    except Exception as e:
        print(f"Error writing to file '{file_path}': {e}")
        sys.exit(1)

def main():
    """
    Main function to execute the QR code decoding process.
    """
    # Prompt the user for the QR code image file path
    qr_image_path = input("Please enter the path to the QR code image (PNG or GIF): ").strip()

    if not os.path.isfile(qr_image_path):
        print(f"Error: '{qr_image_path}' is not a valid file or does not exist.")
        sys.exit(1)

    # Step 1: Read and decode QR codes from the image using OpenCV
    data_list = read_qr_image_opencv(qr_image_path)
    print(f"\nNumber of QR code data parts found: {len(data_list)}")

    # Step 2: Reconstruct the complete Base64 string
    base64_str = reconstruct_base64(data_list)
    print(f"Reconstructed Base64 Data: {base64_str}")

    # Step 3: Decode Base64 to get the original AC code
    ac_string = base64_to_ac(base64_str)
    print(f"Decoded AC Code: {ac_string}")

    # Step 4: Write the AC code to 'ac.txt'
    write_ac_file(ac_string)

if __name__ == "__main__":
    main()
