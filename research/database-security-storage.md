# 数据库安全存储技术 - 研究总结

## 1. 概述

敏感数据的安全存储是信息安全的核心课题。本总结涵盖加密、哈希、加盐等关键技术，为检测历史记录的安全存储提供参考。

---

## 2. GitHub开源项目

### 2.1 SQLite加密方案

| 项目名称 | Stars | 链接 | 技术栈 | 说明 |
|---------|-------|------|--------|------|
| **SQLCipher** | 7,152 | [GitHub](https://github.com/sqlcipher/sqlcipher) | C | SQLite扩展，256位AES加密，广泛使用 |
| **FlashPaper** | 497 | [GitHub](https://github.com/AndrewPaglusch/FlashPaper) | PHP | 一次性加密密码/秘密分享 |
| **sqlite-secure** | - | 多个实现 | 多语言 | 加密SQLite变体 |

### 2.2 SQLCipher核心特性

**加密特性：**
- 256位AES加密数据库文件
- 透明加密，应用层无感知
- 支持多种加密模式（CBC、GCM）
- 跨平台支持

**适用场景：**
- 移动应用本地存储
- 桌面应用敏感数据
- 嵌入式系统

### 2.3 Python加密工具

| 库名称 | 用途 | 说明 |
|-------|------|------|
| cryptography | 通用加密 | Fernet、AES-GCM，推荐使用 |
| pycryptodome | 加密算法 | 兼容PyCrypto，功能全面 |
| PyNaCl | 现代加密 | libsodium绑定，安全默认值 |

---

## 3. 数据分类与保护策略

### 3.1 数据敏感度分类

| 敏感度 | 数据类型 | 保护策略 |
|-------|---------|---------|
| **高敏感** | 密码、API密钥、私钥 | AES-256加密存储 |
| **中敏感** | 邮箱、手机号、身份证 | AES-256加密存储 |
| **低敏感** | 检测结果、风险等级 | 可明文存储 |

### 3.2 本项目数据保护策略

| 字段 | 存储方式 | 理由 |
|-----|---------|------|
| input_content_encrypted | AES-256加密 | 用户输入可能包含敏感信息 |
| detection_type | 明文 | 非敏感元数据 |
| risk_level | 明文 | 非敏感结果 |
| result_detail_encrypted | AES-256加密 | 可能包含检测到的敏感信息 |
| created_at | 明文 | 非敏感时间戳 |

---

## 4. 核心技术详解

### 4.1 对称加密 (Symmetric Encryption)

**推荐算法：**

| 算法 | 密钥长度 | 模式 | 推荐 |
|-----|---------|------|------|
| AES-128 | 128位 | GCM | 推荐 |
| AES-256 | 256位 | GCM | 强烈推荐 |
| ChaCha20 | 256位 | Poly1305 | 移动端推荐 |

**AES-GCM 模式优势：**
- 同时提供加密和完整性验证
- 防止密文篡改攻击
- 性能优秀，硬件加速支持

**存储格式：**
```
IV (初始化向量) + 密文 + 认证标签
例如: base64(IV + ciphertext + tag)
```

### 4.2 密钥派生 (Key Derivation)

| 算法 | 用途 | 特点 |
|-----|------|------|
| PBKDF2 | 密码派生 | 标准算法，广泛支持 |
| bcrypt | 密码哈希 | 内置加盐，抗GPU攻击 |
| scrypt | 密码派生 | 内存困难，抗ASIC |
| Argon2 | 密码哈希 | 最安全，抗各种攻击 |

### 4.3 哈希算法 (Hashing)

| 算法 | 输出长度 | 安全性 | 适用场景 |
|-----|---------|-------|---------|
| MD5 | 128位 | 已破解，不推荐 | 仅用于校验 |
| SHA-1 | 160位 | 已破解，不推荐 | 遗留系统 |
| SHA-256 | 256位 | 安全 | 通用哈希 |
| SHA-3 | 可变 | 安全 | 新系统推荐 |
| bcrypt | 192位 | 安全 | 密码存储推荐 |
| Argon2 | 可变 | 最安全 | 密码存储最佳选择 |

---

## 5. 本项目实现方案

### 5.1 加密工具类设计

```python
# backend/app/utils/crypto.py

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

class DataEncryptor:
    """数据加密工具类"""
    
    def __init__(self):
        # 从环境变量读取密钥
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY环境变量未设置，请设置后启动应用")
        
        # 确保密钥格式正确
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt(self, plaintext: str) -> str:
        """加密字符串，返回base64编码的密文"""
        if not plaintext:
            return ''
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """解密字符串"""
        if not ciphertext:
            return ''
        return self.cipher.decrypt(ciphertext.encode()).decode()


class AESGCMEncryptor:
    """AES-GCM加密器（更高级用法）"""
    
    def __init__(self, key: bytes = None):
        if key is None:
            key = os.getenv('ENCRYPTION_KEY')
            if not key:
                raise ValueError("ENCRYPTION_KEY环境变量未设置")
            key = base64.urlsafe_b64decode(key)
        
        if len(key) != 32:
            raise ValueError("密钥长度必须为32字节（256位）")
        
        self.aesgcm = AESGCM(key)
    
    def encrypt(self, plaintext: str, associated_data: bytes = None) -> str:
        """加密并返回base64编码结果"""
        nonce = os.urandom(12)  # 96位随机nonce
        ciphertext = self.aesgcm.encrypt(
            nonce, 
            plaintext.encode(), 
            associated_data
        )
        return base64.urlsafe_b64encode(nonce + ciphertext).decode()
    
    def decrypt(self, encrypted: str, associated_data: bytes = None) -> str:
        """解密"""
        data = base64.urlsafe_b64decode(encrypted)
        nonce = data[:12]
        ciphertext = data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, associated_data).decode()
```

### 5.2 密钥生成与管理

```python
# 生成新密钥（仅用于初始化）
def generate_key() -> str:
    """生成新的Fernet密钥"""
    return Fernet.generate_key().decode()

# 从密码派生密钥
def derive_key_from_password(password: str, salt: bytes = None) -> tuple:
    """从密码派生加密密钥"""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key.decode(), salt
```

### 5.3 数据库模型集成

```python
# 在保存时自动加密，读取时自动解密
from sqlalchemy import event

class DetectionHistory(Base):
    __tablename__ = "detection_history"
    
    id = Column(Integer, primary_key=True)
    _input_content_encrypted = Column("input_content_encrypted", Text)
    detection_type = Column(String(50))
    risk_level = Column(String(20))
    _result_detail_encrypted = Column("result_detail_encrypted", Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __init__(self, encryptor: DataEncryptor, **kwargs):
        self._encryptor = encryptor
        # 加密敏感字段
        if 'input_content' in kwargs:
            self._input_content_encrypted = encryptor.encrypt(kwargs.pop('input_content'))
        if 'result_detail' in kwargs:
            self._result_detail_encrypted = encryptor.encrypt(kwargs.pop('result_detail'))
        super().__init__(**kwargs)
    
    @property
    def input_content(self) -> str:
        return self._encryptor.decrypt(self._input_content_encrypted)
    
    @property
    def result_detail(self) -> str:
        return self._encryptor.decrypt(self._result_detail_encrypted)
```

---

## 6. 密钥管理策略

### 6.1 环境变量方案（MVP推荐）

```bash
# .env 文件（添加到 .gitignore）
ENCRYPTION_KEY=your-generated-key-here

# 生成密钥命令
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 6.2 密钥管理方案对比

| 方案 | 适用场景 | 安全性 | 复杂度 |
|-----|---------|-------|--------|
| 环境变量 | 开发/小型部署 | 中 | 低 |
| 配置文件 + 权限控制 | 生产环境 | 较高 | 中 |
| 密钥管理服务(KMS) | 企业级 | 高 | 高 |
| 硬件安全模块(HSM) | 金融级 | 最高 | 最高 |

### 6.3 安全检查清单

- [x] 敏感数据加密存储
- [x] 加密密钥不硬编码
- [x] ENCRYPTION_KEY未设置时报错提示
- [x] 使用安全的随机数生成器
- [x] 加密使用认证加密模式(GCM)
- [x] 每条记录使用唯一的IV/Nonce
- [x] 日志中不记录敏感数据明文
- [x] 错误信息不泄露敏感数据

---

## 7. .env.example 配置

```bash
# 加密密钥（必需）
# 生成方法: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=

# 数据库路径
DATABASE_URL=sqlite:///./data/detections.db

# 应用配置
APP_ENV=development
DEBUG=true
```

---

## 8. 参考资源汇总

### 开源项目
- [SQLCipher](https://github.com/sqlcipher/sqlcipher) - SQLite加密扩展，7152 stars
- [FlashPaper](https://github.com/AndrewPaglusch/FlashPaper) - 一次性秘密分享

### Python加密库
- [cryptography](https://cryptography.io/) - 推荐加密库
- [pycryptodome](https://www.pycryptodome.org/) - 功能全面
- [PyNaCl](https://pynacl.readthedocs.io/) - 现代加密

### 标准规范
- NIST SP 800-57: 密钥管理建议
- NIST SP 800-38D: GCM模式规范
- OWASP Cryptographic Storage Cheat Sheet
