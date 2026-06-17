import base64
import hashlib
import os

from cryptography.fernet import Fernet


DEFAULT_ENCRYPTION_SECRET = "danger-detection-system-default-secret"


def _normalize_key(key: str | bytes) -> bytes:
    """Convert an env secret into a valid Fernet key.

    Accepts either:
    - a real Fernet key (32 url-safe base64-encoded bytes)
    - a raw secret, which will be deterministically hashed into a Fernet key
    """

    raw = key.encode() if isinstance(key, str) else key
    try:
        Fernet(raw)
        return raw
    except Exception:
        digest = hashlib.sha256(raw).digest()
        return base64.urlsafe_b64encode(digest)


class DataEncryptor:
    """数据加密工具类 - 使用Fernet(AES-128-CBC + HMAC-SHA256)实现认证加密"""

    def __init__(self):
        key = os.getenv("ENCRYPTION_KEY") or DEFAULT_ENCRYPTION_SECRET
        self.cipher = Fernet(_normalize_key(key))

    def encrypt(self, plaintext: str) -> str:
        """加密字符串，返回base64编码的密文"""
        if not plaintext:
            return ""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """解密base64编码的密文，返回明文字符串"""
        if not ciphertext:
            return ""
        return self.cipher.decrypt(ciphertext.encode()).decode()


def generate_key() -> str:
    """生成新的Fernet密钥（仅用于初始化环境变量）"""
    return Fernet.generate_key().decode()
