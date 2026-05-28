# 敏感信息掩码技术 - 研究总结

## 1. 概述

敏感信息掩码是数据保护的重要手段，用于在展示、存储、传输过程中隐藏或模糊敏感数据，降低数据泄露风险。

---

## 2. API密钥格式参考

### 2.1 常见API密钥格式

| 服务商 | 前缀 | 格式示例 | 正则模式 |
|-------|------|---------|---------|
| OpenAI | `sk-` | `sk-proj-xxxx...` | `sk-[a-zA-Z0-9]{20,}` |
| AWS | `AKIA` | `AKIAIOSFODNN7EXAMPLE` | `AKIA[0-9A-Z]{16}` |
| Google Cloud | `AIza` | `AIzaSyDaGmWKa4JsXZ-H` | `AIza[0-9A-Za-z-_]{35}` |
| GitHub | `ghp_` | `ghp_xxxxxxxxxxxx` | `ghp_[a-zA-Z0-9]{36}` |
| 阿里云 | `LTAI` | `LTAI4xxx...` | `LTAI[0-9A-Za-z]{12,}` |
| 腾讯云 | `AKID` | `AKIDxxxxxxxx` | `AKID[a-zA-Z0-9]{32}` |
| Stripe | `sk_live_` | `sk_live_xxx` | `sk_live_[0-9a-zA-Z]{24}` |
| 通用JWT | - | `eyJhbGciOi...` | `eyJ[a-zA-Z0-9-_]+\.` |

### 2.2 其他敏感信息类型

| 类型 | 正则模式 | 说明 |
|-----|---------|------|
| 邮箱 | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` | 标准邮箱格式 |
| 手机号(中国) | `1[3-9]\d{9}` | 11位手机号 |
| 身份证号 | `\d{17}[\dXx]` | 18位身份证 |
| 银行卡号 | `\d{16,19}` | 16-19位银行卡 |
| 密码字段 | `password\s*[=:]\s*\S+` | 代码中的密码赋值 |
| 私钥标识 | `-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----` | PEM格式私钥 |

---

## 3. 掩码技术分类

### 3.1 静态掩码 (Static Masking)

**定义**：使用固定规则替换敏感数据

| 方法 | 示例 | 适用场景 |
|-----|------|---------|
| 完全隐藏 | `sk-****` | 显示时完全隐藏 |
| 部分显示 | `sk-proj-****xxxx` | 保留前后各4位，便于识别 |
| 字符替换 | `sk-****-****-****` | 固定长度掩码 |
| 哈希替换 | `sk-a1b2c3d4` | 使用哈希值替换 |

**推荐实现**：
```
原始: sk-proj-abc123def456ghi789jkl
掩码: sk-proj-****789jkl (保留前缀和后4位)
```

### 3.2 动态掩码 (Dynamic Masking)

**定义**：根据用户权限、上下文动态决定掩码策略

| 场景 | 掩码策略 |
|-----|---------|
| 普通用户查看 | 完全隐藏 |
| 管理员查看 | 部分显示 |
| 系统内部处理 | 不掩码 |
| 日志记录 | 完全隐藏 |

### 3.3 可逆掩码 (Reversible Masking)

**定义**：掩码后可通过密钥恢复原始数据

| 方法 | 说明 |
|-----|------|
| 加密掩码 | 使用AES加密，存储密文 |
| 格式保留加密(FPE) | 加密后保持原格式，如银行卡号加密后仍是数字 |
| 令牌化(Tokenization) | 用随机令牌替换敏感数据，映射表单独存储 |

---

## 4. 推荐掩码方案

### 4.1 显示掩码建议

```
API密钥: sk-proj-abc...xyz → sk-proj-****xyz (保留前缀和后3位)
邮箱: user@example.com → u***@example.com (保留首字母和域名)
手机号: 13812345678 → 138****5678 (保留前3后4位)
身份证: 110101199001011234 → 110101********1234 (保留前6后4位)
密码字段: password=admin123 → password=****** (完全隐藏)
```

### 4.2 存储掩码建议

| 数据类型 | 存储方式 |
|---------|---------|
| 检测输入内容 | 使用AES-256加密存储 |
| 密码检测结果 | 仅存储风险等级和建议，不存储密码原文 |
| API密钥检测结果 | 存储掩码后的值用于记录 |

---

## 5. 代码实现参考

### 5.1 Python掩码函数示例

```python
import re

def mask_api_key(value: str) -> str:
    """API密钥掩码：保留前缀和后3位"""
    if len(value) <= 10:
        return '*' * len(value)
    prefix = value[:7] if value.startswith('sk-') else value[:4]
    suffix = value[-3:]
    return f"{prefix}****{suffix}"

def mask_email(email: str) -> str:
    """邮箱掩码：保留首字母和域名"""
    parts = email.split('@')
    if len(parts) != 2:
        return '***@***.***'
    username, domain = parts
    masked_user = username[0] + '*' * (len(username) - 1)
    return f"{masked_user}@{domain}"

def mask_phone(phone: str) -> str:
    """手机号掩码：保留前3后4位"""
    if len(phone) != 11:
        return '***-****-****'
    return f"{phone[:3]}****{phone[7:]}"
```

---

## 6. 安全建议

1. **最小化存储**：检测完成后尽量不保留原始敏感数据
2. **分级掩码**：根据数据敏感度选择不同掩码策略
3. **日志脱敏**：确保日志中不记录明文敏感信息
4. **传输加密**：API响应中使用掩码值，不返回原文

---

## 7. 参考标准

- PCI DSS: 支付卡行业数据安全标准
- GDPR: 通用数据保护条例
- NIST SP 800-122: 个人身份信息保护指南
- OWASP Top 10: 敏感数据暴露防护
