#!/usr/bin/env python3
"""
- Converts the data inside 'ac.txt' to Base64 and saves it as a WAV audio file.
- Represents each Base64 character with a specific frequency.
- Install required packages with:
    pip install numpy soundfile
"""

import numpy as np
import soundfile as sf
import base64
import sys

# Settings
SAMPLE_RATE = 44100      # 44.1kHz sample rate
BIT_DURATION = 0.05      # Duration per Base64 character (seconds)
AMPLITUDE = 0.5          # Volume level (0.0 - 1.0)

# Frequency assignment for Base64 characters
BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
FREQ_START = 300         # Starting frequency (Hz)
FREQ_STEP = 50           # Frequency increment per character

def read_ac_file(file_path):
    """
    Reads the 'ac.txt' file and returns its content as a string.

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
    """
    try:
        base64_str = base64.b64encode(ac_string.encode('utf-8')).decode('utf-8')
        return base64_str
    except Exception as e:
        print(f"Error during Base64 conversion: {e}")
        sys.exit(1)

def generate_tone(frequency, duration, sample_rate=SAMPLE_RATE, amplitude=AMPLITUDE):
    """
    Generates a sine wave tone at a specific frequency.

    Args:
        frequency (float): Frequency of the tone in Hz.
        duration (float): Duration of the tone in seconds.
        sample_rate (int, optional): Sampling rate in Hz. Defaults to SAMPLE_RATE.
        amplitude (float, optional): Amplitude of the tone (0.0 - 1.0). Defaults to AMPLITUDE.

    Returns:
        np.ndarray: The generated sine wave as a NumPy array.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t)

def generate_audio_from_base64(base64_str):
    """
    Generates audio tones from a Base64 string by mapping each character to a frequency.

    Args:
        base64_str (str): The Base64-encoded string.

    Returns:
        np.ndarray: The concatenated audio waveform representing the entire Base64 string.
    """
    tones = []
    for char in base64_str:
        if char in BASE64_CHARS:
            freq = FREQ_START + BASE64_CHARS.index(char) * FREQ_STEP
            tone = generate_tone(freq, BIT_DURATION)
            tones.append(tone)
            print(f"Frequency for character '{char}': {freq} Hz")
        else:
            print(f"Warning: Character '{char}' is not a valid Base64 character and will be skipped.")
    if tones:
        return np.concatenate(tones)
    else:
        print("Error: No valid Base64 characters found to generate audio.")
        sys.exit(1)

def save_audio_to_wav(audio_waveform, file_path="ac_audio.wav", sample_rate=SAMPLE_RATE):
    """
    Saves the audio waveform to a WAV file.

    Args:
        audio_waveform (np.ndarray): The audio waveform to save.
        file_path (str, optional): The filename for the saved WAV file. Defaults to "ac_audio.wav".
        sample_rate (int, optional): The sample rate in Hz. Defaults to SAMPLE_RATE.

    Raises:
        SystemExit: If saving the file fails.
    """
    try:
        sf.write(file_path, audio_waveform, sample_rate)
        print(f"Audio successfully saved as '{file_path}'.")
    except Exception as e:
        print(f"Error saving audio file '{file_path}': {e}")
        sys.exit(1)

def main():
    """
    Main function to execute the AC to audio conversion process.
    """
    # 1) Read the AC file
    ac_string = read_ac_file("ac.txt")
    print(f"Original AC Content: {ac_string}")

    # 2) Convert AC to Base64
    base64_encoded = ac_to_base64(ac_string)
    print(f"Base64 Encoded Data: {base64_encoded}")

    # 3) Convert Base64 string to audio
    audio_waveform = generate_audio_from_base64(base64_encoded)

    # 4) Save the audio waveform to a WAV file
    save_audio_to_wav(audio_waveform, file_path="ac_audio.wav")

if __name__ == "__main__":
    main()
