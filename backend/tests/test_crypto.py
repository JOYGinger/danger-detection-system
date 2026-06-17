import os
import pytest
from cryptography.fernet import Fernet
from app.utils.crypto import DataEncryptor, generate_key


class TestDataEncryptor:

    def setup_method(self):
        self.key = Fernet.generate_key().decode()
        os.environ['ENCRYPTION_KEY'] = self.key
        self.encryptor = DataEncryptor()

    def teardown_method(self):
        os.environ.pop('ENCRYPTION_KEY', None)

    def test_encrypt_decrypt_roundtrip(self):
        plaintext = "这是一段测试文本"
        ciphertext = self.encryptor.encrypt(plaintext)
        assert ciphertext != plaintext
        assert self.encryptor.decrypt(ciphertext) == plaintext

    def test_encrypt_empty_string(self):
        assert self.encryptor.encrypt('') == ''

    def test_decrypt_empty_string(self):
        assert self.encryptor.decrypt('') == ''

    def test_chinese_content(self):
        plaintext = "您的账户存在异常，请立即点击链接验证身份"
        ciphertext = self.encryptor.encrypt(plaintext)
        assert self.encryptor.decrypt(ciphertext) == plaintext

    def test_long_text(self):
        plaintext = "A" * 10000
        ciphertext = self.encryptor.encrypt(plaintext)
        assert self.encryptor.decrypt(ciphertext) == plaintext

    def test_special_characters(self):
        plaintext = "password=admin123\nemail=test@example.com\t<>&\"'"
        ciphertext = self.encryptor.encrypt(plaintext)
        assert self.encryptor.decrypt(ciphertext) == plaintext

    def test_different_encryptions_differ(self):
        plaintext = "相同内容"
        c1 = self.encryptor.encrypt(plaintext)
        c2 = self.encryptor.encrypt(plaintext)
        assert c1 != c2
        assert self.encryptor.decrypt(c1) == self.encryptor.decrypt(c2)

    def test_missing_encryption_key(self):
        os.environ.pop('ENCRYPTION_KEY', None)
        with pytest.raises(ValueError, match="ENCRYPTION_KEY"):
            DataEncryptor()

    def test_invalid_ciphertext(self):
        from cryptography.fernet import InvalidToken
        with pytest.raises(InvalidToken):
            self.encryptor.decrypt("invalid-ciphertext")


class TestGenerateKey:

    def test_generate_key_format(self):
        key = generate_key()
        assert isinstance(key, str)
        Fernet(key.encode())

    def test_generate_key_unique(self):
        k1 = generate_key()
        k2 = generate_key()
        assert k1 != k2
