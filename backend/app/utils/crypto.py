import os
from cryptography.fernet import Fernet


class DataEncryptor:
    """数据加密工具类 - 使用Fernet(AES-128-CBC + HMAC-SHA256)实现认证加密"""

    def __init__(self):
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY环境变量未设置，请设置后启动应用")
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, plaintext: str) -> str:
        """加密字符串，返回base64编码的密文"""
        if not plaintext:
            return ''
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """解密base64编码的密文，返回明文字符串"""
        if not ciphertext:
            return ''
        return self.cipher.decrypt(ciphertext.encode()).decode()


def generate_key() -> str:
    """生成新的Fernet密钥（仅用于初始化环境变量）"""
    return Fernet.generate_key().decode()
