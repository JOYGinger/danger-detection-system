# 数据库安全存储技术 - 研究总结

## 1. 概述

敏感数据的安全存储是信息安全的核心课题。本总结涵盖加密、哈希、加盐等关键技术，为检测历史记录的安全存储提供参考。

---

## 2. 数据分类与保护策略

### 2.1 数据敏感度分类

| 敏感度 | 数据类型 | 保护策略 |
|-------|---------|---------|
| **高敏感** | 密码、API密钥、私钥 | 加盐哈希 / AES加密 |
| **中敏感** | 邮箱、手机号、身份证 | AES加密存储 |
| **低敏感** | 检测结果、风险等级 | 可明文存储 |

### 2.2 本项目数据保护策略

| 字段 | 存储方式 | 理由 |
|-----|---------|------|
| input_content | AES-256加密 | 用户输入可能包含敏感信息 |
| detection_type | 明文 | 非敏感元数据 |
| risk_level | 明文 | 非敏感结果 |
| result_detail | AES-256加密 | 可能包含检测到的敏感信息 |
| created_at | 明文 | 非敏感时间戳 |

---

## 3. 核心技术详解

### 3.1 哈希算法 (Hashing)

**原理**：单向函数，将任意长度输入转换为固定长度输出

| 算法 | 输出长度 | 安全性 | 适用场景 |
|-----|---------|-------|---------|
| MD5 | 128位 | 已破解，不推荐 | 仅用于校验 |
| SHA-1 | 160位 | 已破解，不推荐 | 遗留系统 |
| SHA-256 | 256位 | 安全 | 通用哈希 |
| SHA-3 | 可变 | 安全 | 新系统推荐 |
| bcrypt | 192位 | 安全 | 密码存储推荐 |
| Argon2 | 可变 | 最安全 | 密码存储最佳选择 |

**问题**：彩虹表攻击 - 预计算的哈希值表可反向查找

### 3.2 加盐 (Salting)

**原理**：在哈希前添加随机值，防止彩虹表攻击

```
原始密码: mypassword
随机盐值: x7K9mP2q
加盐后: mypasswordx7K9mP2q
哈希值: $2b$12$x7K9mP2q... (bcrypt格式)
```

**存储格式**：
```
盐值 + 哈希值
例如: x7K9mP2q$2b$12$LQv3c1yqBWVHxkd0...
```

**最佳实践**：
- 盐值长度 ≥ 16字节
- 每条记录使用唯一盐值
- 使用密码学安全随机数生成器(CSPRNG)

### 3.3 对称加密 (Symmetric Encryption)

**原理**：使用相同密钥加密和解密

| 算法 | 密钥长度 | 模式 | 推荐 |
|-----|---------|------|------|
| AES-128 | 128位 | GCM | 推荐 |
| AES-256 | 256位 | GCM | 强烈推荐 |
| ChaCha20 | 256位 | Poly1305 | 移动端推荐 |

**AES-GCM 模式优势**：
- 同时提供加密和完整性验证
- 防止密文篡改攻击
- 性能优秀，硬件加速支持

**存储格式**：
```
IV (初始化向量) + 密文 + 认证标签
例如: base64(IV + ciphertext + tag)
```

### 3.4 密钥派生 (Key Derivation)

**原理**：从用户密码派生加密密钥

| 算法 | 用途 | 特点 |
|-----|------|------|
| PBKDF2 | 密码派生 | 标准算法，广泛支持 |
| bcrypt | 密码哈希 | 内置加盐，抗GPU攻击 |
| scrypt | 密码派生 | 内存困难，抗ASIC |
| Argon2 | 密码哈希 | 最安全，抗各种攻击 |

---

## 4. 本项目推荐方案

### 4.1 存储架构

```
用户输入 (明文)
    ↓
检测处理 (内存中)
    ↓
存储前加密
    ↓
┌─────────────────────────────────────┐
│  AES-256-GCM 加密                   │
│  - 密钥: 从配置文件读取或派生        │
│  - IV: 每次随机生成12字节            │
│  - 附加数据: 记录ID (防篡改)         │
└─────────────────────────────────────┘
    ↓
数据库存储 (密文)
```

### 4.2 加密工具推荐

```python
# 推荐使用 cryptography 库
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 或使用 pycryptodome
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
```

### 4.3 密钥管理

| 方案 | 适用场景 | 安全性 |
|-----|---------|-------|
| 环境变量 | 开发环境 | 中 |
| 配置文件 + 权限控制 | 生产环境 | 较高 |
| 密钥管理服务(KMS) | 企业级 | 最高 |
| 硬件安全模块(HSM) | 金融级 | 最高 |

**MVP阶段建议**：
- 使用环境变量存储主密钥
- 应用启动时读取，不硬编码
- `.env` 文件添加到 `.gitignore`

---

## 5. 实现参考

### 5.1 加密工具类设计

```python
# backend/app/utils/crypto.py

from cryptography.fernet import Fernet
import os
import base64

class DataEncryptor:
    def __init__(self):
        # 从环境变量读取密钥，或生成新密钥
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key().decode()
        self.cipher = Fernet(key.encode())
    
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
```

### 5.2 数据库模型集成

```python
# 在保存时自动加密，读取时自动解密
class EncryptedField:
    def __init__(self, encryptor: DataEncryptor):
        self.encryptor = encryptor
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj._encrypted_data
        return self.encryptor.decrypt(value) if value else None
    
    def __set__(self, obj, value):
        obj._encrypted_data = self.encryptor.encrypt(value) if value else ''
```

---

## 6. 安全检查清单

- [ ] 敏感数据加密存储
- [ ] 加密密钥不硬编码
- [ ] 使用安全的随机数生成器
- [ ] 加密使用认证加密模式(GCM)
- [ ] 每条记录使用唯一的IV
- [ ] 日志中不记录敏感数据明文
- [ ] 错误信息不泄露敏感数据

---

## 7. 参考资源

- NIST SP 800-57: 密钥管理建议
- NIST SP 800-38D: GCM模式规范
- OWASP Cryptographic Storage Cheat Sheet
- Python cryptography 库文档: https://cryptography.io/
