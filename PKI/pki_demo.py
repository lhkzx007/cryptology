from Crypto import Random  # 随机数算法
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cpkc  # 加密 PKI标准 算法
from Crypto.Signature import PKCS1_v1_5 as Spkc  # 签名 PKI标准 算法
from Crypto.PublicKey import RSA
import base64

from enum import Enum


class FileName(Enum):
    PRIVATE = "master-private.pem"
    PUBLIC = "master-public.pem"


class PKI:
    def __init__(self):
        self.random_maker = None
        self.rsa = None
        self.makePem()

    def makePem(self):
        self.random_maker = Random.new().read()
        # 获取算法实例
        self.rsa = RSA.generate(1024, self.random_maker)

        # 生成私钥 并保存到文件
        private_pem = self.rsa.exportKey()
        # 保存私钥与公钥到文件'
        with open(FileName.PRIVATE.value, "wb") as file:
            file.write(private_pem)

        # 生成公钥 并保存到文件
        public_pem = self.rsa.publickey().exportKey()
        with open(FileName.PUBLIC.value, "wb") as file:
            file.write(public_pem)

    # 加密  公钥加密
    def encode(self, message):
        with open(FileName.PUBLIC.value, "rb") as file:
            key = file.read()
            rsa_Key = RSA.importKey(key)
            crypt = Cpkc.new(rsa_Key). \
                encrypt(message.encode())
            print(crypt)
            msg = base64.b64encode(crypt)
            print("加密 :", msg)
            return msg

    # 解密 私钥解密
    def decode(self, crypt_msg):
        with open(FileName.PRIVATE.value, "rb") as file:
            key = file.read()
            rsa_Key = RSA.importKey(key)
            crypt = Cpkc.new(rsa_Key). \
                decrypt(base64.b64decode(crypt_msg), self.random_maker)
            print("解密 :", crypt.decode())

    # 签名 , 使用私钥生成签名
    def signal(self, message):
        with open(FileName.PRIVATE.value, "rb") as file:
            key = file.read()  # 读取文件内容
            rsa_key = RSA.importKey(key)  # 从文件内容中获取key
            signer = Spkc.new(rsa_key)  # 创建签名工具
            digest = SHA.new()  # 创建签名算法
            digest.update(message)  # 导入需要签名的数据
            sign = signer.sign(digest)  # 对数据进行签名
            signature = base64.b64encode(sign)
            print("signature", signature)
            return signature

    # 验证 , 使用公钥进行验证
    def verify(self, message):
        with open(FileName.PUBLIC.value, "rb") as file:
            key = file.read()
            rsa_key = RSA.importKey(key)
            signer = Spkc.new(rsa_key)
            digest = SHA.new()
            digest.update("zack:寂静岭就说了几句".encode())
            print(signer.verify(digest, base64.b64decode(message)))


if __name__ == "__main__":
    pki = PKI()
    msg = pki.encode("zack:寂静岭就说了几句")
    pki.decode(msg)
    sinsss = pki.signal("zack:寂静岭就说了几句".encode())
    pki.verify(sinsss)
