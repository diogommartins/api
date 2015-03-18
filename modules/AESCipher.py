# coding=utf-8
from Crypto import Random
from Crypto.Cipher import AES

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]
# TODO Essa chave não deveria estar exposta no módulo
key = "36396F723576455432413134726279644437314F4B59583564416A686B475255"


class AESCipher:
    def __init__(self, key=key):
        """
        Requires hex encoded param as a key
        """
        self.key = key.decode("hex")

    def encrypt(self, raw):
        """
        Returns hex encoded encrypted value!
        """
        raw = pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return (iv + cipher.encrypt(raw)).encode("hex")

    def decrypt(self, enc):
        """
        Requires hex encoded param to decrypt
        """
        enc = enc.decode("hex")
        iv = enc[:16]
        enc = enc[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc))


if __name__ == "__main__":
    key = "36396F723576455432413134726279644437314F4B59583564416A686B475255"
    ciphertext = "ef1253d42e9c510b3fde95b7b17e6944a3077c09eeb65f7bb6148719204e3732";
    key = key[:32]
    decryptor = AESCipher(key)
    plaintext = decryptor.decrypt(ciphertext)
    print "%s" % plaintext