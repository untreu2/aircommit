# **AirCommit: Verifiable Data Transmission Protocol for Offline Environments**

## **Abstract**

AirCommit is a protocol designed to provide secure, portable, and verifiable data transmission for devices that must remain offline. Initially developed for updates (git commits), it has evolved into a comprehensive data transmission solution. The protocol uses digital signatures, encoding techniques, and offline data transmission methods to ensure data integrity and reliability. **This enables data transmission via QR codes, sound waves, and other offline methods without requiring any connection**.

---

## **1. Introduction**

Modern data transmission methods often rely on internet connectivity. Even when a direct internet connection is not required, the sender and offline device must still establish a link, which introduces security risks for sensitive devices. Data transmission to offline devices, especially in security-critical systems (such as Bitcoin cold wallets), must be both verifiable and portable.

AirCommit is developed to enable secure data transmission to offline devices. The protocol simplifies the transport and verification of data for offline environments.

---

## **2. Objectives of the Protocol**

### **2.1. Data Security**
- Ensuring data integrity and preventing unauthorized modifications.
- Verifying the sender's identity through digital signatures.

### **2.2. Offline Portability**
- Enabling data transmission without requiring an online/offline connection between devices.
- Supporting QR codes, sound waves, and physical transport methods.

### **2.3. General Applicability**
- Allowing devices that must remain offline to receive data without connecting to internet-enabled devices.
- Providing flexibility to work with any type of data.

---

## **3. Technical Details**

### **3.1. Elliptic Curve Cryptography (ECC)**

AirCommit leverages **Elliptic Curve Cryptography (ECC)** to provide a secure mechanism for key generation and digital signatures.

#### **3.1.1. ECDSA (secp256k1)**

AirCommit uses the **secp256k1** elliptic curve, which is widely used in secure systems like Bitcoin due to its high speed and robust security.

- **Private Key:**  
  A randomly generated 256-bit value used to sign files.  
  Format: `acsec1...`

- **Public Key:**  
  A 512-bit key (consisting of X and Y coordinates) derived from the private key and used to verify signatures.  
  Format: `acpub1...`


### **3.2. Data Signing and Verification**

AirCommit ensures secure data transmissions through digital signatures. The signing process follows these steps:

1. **Preparing the File:**  
   - The file to be transmitted is encoded in Base64 format.

2. **Signing:**  
   - The encoded file is signed using the private key.

3. **Verification:**  
   - The recipient verifies the signature using the public key to confirm that the file has not been altered.

4. **Mnemonic Verification (Optional):**  
   - The AC code can be hashed using SHA-256 to generate mnemonic words, which can be used in the verification process.

---

### **3.3. Data Encoding**

- **Bech32:**  
  Keys and signatures are stored in Bech32 format.  
  Example: `acsec1qxyz...` or `acpub1rxyz...`

- **Base64:**  
  File content is encoded in Base64 to make it portable.  
  Example: `MTIzNDU2Nzg5L2Jhc2U2NA==`

---

### **3.4. AC Code Format**

AirCommit uses the **ac** format to combine all data and signatures into a single line. The file to be transmitted is encoded in Base64 and merged with the digital signature.

**Format:**

```
ac{Base64_encoded_data}{acsig1...}
```

**Example:**

```
acU2FtcGxlIGRhdGEgdG8gYmUgc2lnbmVkIHdpdGggQUlSQ09NTUlUacsig1qw8v0...
```

---

### **3.5. QR Code Formatting**

Large files are split into multiple QR codes for transmission. The QR codes are formatted as follows:

```
{part_number}P{total_parts}QR: {Base64_encoded_ac}
```

**Example:**

```
1P5QR: U29tZSBzYW1wbGUgZGF0YS4uLg==
2P5QR: Q29udGludWVkIGRhdGEuLg==
```

This structure ensures the correct sequential scanning of QR codes and detects missing parts.

---

### **3.6. Audio Formatting**

Data files can be transmitted using audio signals by converting their content into Base64 format and representing each character as a unique frequency. 

The encoded Base64 string `{Base64_encoded_ac}` is processed as follows:

3. **Frequency Mapping:**  
   Each character in `{Base64_encoded_ac}` is assigned a specific frequency:
   
   - **Character Set:** `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=`
   - **Starting Frequency:** 300 Hz
   - **Frequency Step:** 50 Hz per character

4. **Audio Generation:**  
   A sine wave tone is generated for each character in `{Base64_encoded_ac}` using the formula:

   ```
   amplitude * sin(2 * π * frequency * time)
   ```

   The tones are concatenated to form a continuous audio waveform.

5. **Playback and Transmission:**  
   The generated audio signal is played for transmission or stored for further use.

**Example Audio Encoding:**

Given the Base64 encoded string:

```
U29tZSBzYW1wbGUgZGF0YS4uLg==
```

The corresponding audio signal will represent each character with its mapped frequency and be played sequentially.

---

## **4. Conclusion**

AirCommit provides a secure and verifiable way to transmit data to devices that do not need internet connectivity. Using digital signatures and various offline transmission methods, it ensures data integrity and safe delivery in critical environments.

*Written by untreu (Emir Yorulmaz), [GitHub Repository](https://github.com/untreu2/aircommit)*

*Date: 2025-01-26*
