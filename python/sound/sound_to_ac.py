#!/usr/bin/env python3
"""
- Reads an audio file where each Base64 character is represented by a specific frequency.
- Detects frequencies in the audio to reconstruct the Base64 string.
- Decodes the Base64 string to retrieve the original AC code.
- Writes the AC code to 'ac.txt'.
- Prompts the user to input the audio file path interactively.
- Install required packages with:
    pip install numpy scipy soundfile
"""

import numpy as np
import soundfile as sf
import sys
import os
import math
import base64
from scipy.signal import find_peaks
from scipy.fft import fft, fftfreq

# Settings (These should match the encoding settings)
SAMPLE_RATE = 44100          # 44.1kHz sample rate
BIT_DURATION = 0.05          # Duration per Base64 character (seconds)
AMPLITUDE_THRESHOLD = 0.1    # Minimum amplitude to consider a peak valid
FREQ_TOLERANCE = 10          # Tolerance in Hz for frequency matching

# Frequency assignment for Base64 characters (Must match the encoding)
BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
FREQ_START = 300             # Starting frequency (Hz)
FREQ_STEP = 50               # Frequency increment per character

def read_audio_file(file_path):
    """
    Reads the audio file and returns the audio data and sample rate.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        tuple: (audio_data as numpy array, sample_rate)

    Raises:
        SystemExit: If the file is not found or cannot be read.
    """
    try:
        data, samplerate = sf.read(file_path)
        # If stereo, take only one channel
        if len(data.shape) == 2:
            data = data[:, 0]
        return data, samplerate
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading audio file '{file_path}': {e}")
        sys.exit(1)

def split_audio_into_bits(audio_data, sample_rate, bit_duration):
    """
    Splits the audio data into segments corresponding to each Base64 character.

    Args:
        audio_data (numpy array): The audio waveform data.
        sample_rate (int): The sample rate of the audio data.
        bit_duration (float): Duration of each Base64 character in seconds.

    Returns:
        list of numpy arrays: Each array corresponds to a segment representing one character.
    """
    samples_per_bit = int(sample_rate * bit_duration)
    total_bits = math.ceil(len(audio_data) / samples_per_bit)
    segments = []
    for i in range(total_bits):
        start = i * samples_per_bit
        end = start + samples_per_bit
        segment = audio_data[start:end]
        # If the last segment is shorter, pad it with zeros
        if len(segment) < samples_per_bit:
            segment = np.pad(segment, (0, samples_per_bit - len(segment)), 'constant')
        segments.append(segment)
    return segments

def detect_frequency(segment, sample_rate):
    """
    Detects the dominant frequency in an audio segment using FFT.

    Args:
        segment (numpy array): The audio segment.
        sample_rate (int): The sample rate of the audio data.

    Returns:
        float: The detected dominant frequency in Hz.

    Raises:
        ValueError: If no significant frequency is detected.
    """
    # Perform FFT
    N = len(segment)
    yf = fft(segment)
    xf = fftfreq(N, 1 / sample_rate)

    # Take the positive frequencies
    idxs = np.where(xf > 0)
    xf = xf[idxs]
    yf = np.abs(yf[idxs])

    # Find the peak frequency
    peak_idx, _ = find_peaks(yf, height=AMPLITUDE_THRESHOLD * np.max(yf))
    if len(peak_idx) == 0:
        raise ValueError("No significant peak found.")
    # Take the first peak
    peak_freq = xf[peak_idx[0]]
    return peak_freq

def map_frequency_to_base64_char(frequency):
    """
    Maps a detected frequency to its corresponding Base64 character.

    Args:
        frequency (float): The detected frequency in Hz.

    Returns:
        str: The corresponding Base64 character.

    Raises:
        ValueError: If the frequency does not match any Base64 character.
    """
    # Calculate the expected frequency for each Base64 character
    for index, char in enumerate(BASE64_CHARS):
        expected_freq = FREQ_START + index * FREQ_STEP
        if abs(frequency - expected_freq) <= FREQ_TOLERANCE:
            return char
    raise ValueError(f"Frequency {frequency:.2f} Hz does not match any Base64 character.")

def reconstruct_base64_string(char_list):
    """
    Reconstructs the Base64 string from a list of characters.

    Args:
        char_list (list of str): List of Base64 characters.

    Returns:
        str: The complete Base64-encoded string.
    """
    return ''.join(char_list)

def decode_base64(base64_str):
    """
    Decodes the Base64 string to retrieve the original AC string.

    Args:
        base64_str (str): The Base64-encoded string.

    Returns:
        str: The decoded AC string.

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
    Main function to execute the audio decoding process.
    """
    # Prompt the user for the audio file path
    audio_file_path = input("Please enter the path to the audio file (e.g., ac_audio.wav): ").strip()

    if not os.path.isfile(audio_file_path):
        print(f"Error: '{audio_file_path}' is not a valid file or does not exist.")
        sys.exit(1)

    # Step 1: Read the audio file
    audio_data, samplerate = read_audio_file(audio_file_path)
    print(f"\nAudio file '{audio_file_path}' loaded.")
    print(f"Sample rate: {samplerate} Hz")
    print(f"Total samples: {len(audio_data)}\n")

    # Step 2: Split audio into segments representing each Base64 character
    segments = split_audio_into_bits(audio_data, samplerate, BIT_DURATION)
    print(f"Audio split into {len(segments)} segments based on bit duration of {BIT_DURATION} seconds.\n")

    # Step 3: Detect frequencies and map to Base64 characters
    base64_chars = []
    for i, segment in enumerate(segments):
        try:
            freq = detect_frequency(segment, samplerate)
            char = map_frequency_to_base64_char(freq)
            base64_chars.append(char)
            print(f"Segment {i+1}: Detected Frequency = {freq:.2f} Hz -> '{char}'")
        except ValueError as ve:
            print(f"Segment {i+1}: {ve} Skipping this segment.")

    if not base64_chars:
        print("\nError: No valid Base64 characters were decoded from the audio.")
        sys.exit(1)

    # Step 4: Reconstruct Base64 string
    base64_str = reconstruct_base64_string(base64_chars)
    print(f"\nReconstructed Base64 String: {base64_str}\n")

    # Step 5: Decode Base64 to get the original AC string
    ac_string = decode_base64(base64_str)
    print(f"Decoded AC String: {ac_string}\n")

    # Step 6: Write the AC string to 'ac.txt'
    write_ac_file(ac_string)

if __name__ == "__main__":
    main()
