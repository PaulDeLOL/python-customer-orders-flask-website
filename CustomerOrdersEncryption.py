"""
Name: Pablo Guardia
Date: 03/31/2025
Assignment: Module 12: Encrypt Data in database
Due Date: 04/06/2025

About this project: This script is an implementation of an
encryption/decryption class in order to provide encryption functionality to
the Customer Orders Flask website. The code is based on an encryption
mechanism I used together with my team in CEN4090L: Software Engineering
Capstone as part of our software project for that class, which was also a
Flask website.

Assumptions: N/A
All work below was performed by Pablo Guardia
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import Padding


class AESCipher(object):
    def __init__(self, key,iv):
        self.key = key
        self.iv = iv

    def encrypt(self, plaintext):
        cipher_function = Cipher(algorithms.AES(self.key), modes.CBC(self.iv))
        encryptor = cipher_function.encryptor()

        plaintext = Padding.appendPadding(plaintext, blocksize
        = Padding.AES_blocksize, mode = 'CBC')
        raw = bytes(plaintext, 'utf-8')
        ciphertext = encryptor.update(raw) + encryptor.finalize()

        return ciphertext

    def decrypt(self, ciphertext):
        cipher_function = Cipher(algorithms.AES(self.key), modes.CBC(self.iv))
        decryptor = cipher_function.decryptor()

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        plaintext = str(plaintext, 'utf-8')
        plaintext = Padding.removePadding(plaintext, mode = 'CBC')

        return plaintext


key = b"QAIOKaA8OTFis-PV6tYw0GDkkGS86Ea8"
iv = b"U9r7ZyoMoEs=OWFJ"
cipher = AESCipher(key, iv)


if __name__ == "__main__":
    original = "This is a testing message!"
    print(original)
    encrypted = cipher.encrypt(original)
    print(encrypted)
    decrypted = cipher.decrypt(encrypted)
    print(decrypted)
