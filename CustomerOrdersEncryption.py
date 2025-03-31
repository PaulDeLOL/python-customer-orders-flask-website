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
