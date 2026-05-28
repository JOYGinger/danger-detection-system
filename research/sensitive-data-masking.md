# 敏感信息掩码技术 - 研究总结

## 1. 概述

敏感信息掩码是数据保护的重要手段，用于在展示、存储、传输过程中隐藏或模糊敏感数据，降低数据泄露风险。

---

## 2. 学术论文资源（arXiv）

### 2.1 PII检测与隐私保护论文

| 论文标题 | 年份 | 链接 | 核心贡献 |
|---------|------|------|---------|
| PII-Bench: Evaluating Query-Aware Privacy Protection Systems | 2025 | [arXiv:2502.18545](https://arxiv.org/abs/2502.18545) | 首个PII保护评估框架，55种PII类别，2842测试样本 |
| PII-Scope: A Comprehensive Study on Training Data PII Extraction Attacks in LLMs | 2024 | [arXiv:2410.06704](https://arxiv.org/abs/2410.06704) | LLM中PII提取攻击研究，攻击成功率可提升5倍 |
| SoK: Differential Privacies | 2019 | [arXiv:1906.01337](https://arxiv.org/abs/1906.01337) | 差分隐私系统性分类，7大变体分析 |

### 2.2 关键技术发现

**PII-Bench (2025) 重要发现：**
- 定义了55种细粒度PII类别
- 现有模型在PII检测上表现良好
- 但在判断PII与查询相关性方面存在显著局限
- 多主体复杂场景处理能力不足

**PII-Scope (2024) 攻击研究：**
- 预训练模型PII泄露被低估
- 高级对抗策略可使提取率提升5倍
- 微调模型比预训练模型更脆弱

---

## 3. GitHub开源项目

### 3.1 PII检测工具

| 项目名称 | Stars | 链接 | 技术栈 | 说明 |
|---------|-------|------|--------|------|
| **earlybird** | 770 | [GitHub](https://github.com/americanexpress/earlybird) | Go | 美国运通开源，扫描源代码中的密码、PII、弱加密、密钥文件 |
| **pii-masker** | 168 | [GitHub](https://github.com/HydroXai/pii-masker) | Python | 基于DeBERTa-v3的AI掩码工具，高精度检测 |
| **safe-zone** | 26 | [GitHub](https://github.com/thyrisAI/safe-zone) | Go | PII检测护栏引擎，防止敏感数据泄露到LLM |
| **cipher-gate** | 11 | [GitHub](https://github.com/PkLavc/cipher-gate) | Python | 动态数据掩码(DDM)、AES-256加密、HIPAA/GDPR合规 |
| **piihunter** | 6 | [GitHub](https://github.com/offensivedev/piihunter) | Go | 扫描代码中的明文密码、Token、邮箱、手机号等 |
| **pii-shield** | 3 | [GitHub](https://github.com/swissprismia/pii-shield) | Rust | 系统级剪贴板PII检测，100%离线运行 |

### 3.2 推荐参考实现

**earlybird (美国运通)** 值得借鉴的特性：
- 支持多种敏感信息类型检测
- 可扩展的规则引擎
- 支持Git历史扫描
- 输出格式灵活（JSON、SARIF）

**pii-masker (DeBERTa)** AI方法：
- 使用DeBERTa-v3模型
- 高精度NLP检测
- Python API易于集成

---

## 4. API密钥格式参考

### 4.1 常见API密钥格式

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

### 4.2 其他敏感信息类型

| 类型 | 正则模式 | 说明 |
|-----|---------|------|
| 邮箱 | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` | 标准邮箱格式 |
| 手机号(中国) | `1[3-9]\d{9}` | 11位手机号 |
| 身份证号 | `\d{17}[\dXx]` | 18位身份证 |
| 银行卡号 | `\d{16,19}` | 16-19位银行卡 |
| 密码字段 | `password\s*[=:]\s*\S+` | 代码中的密码赋值 |
| 私钥标识 | `-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----` | PEM格式私钥 |

---

## 5. 掩码技术分类

### 5.1 静态掩码 (Static Masking)

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

### 5.2 动态掩码 (Dynamic Masking)

**定义**：根据用户权限、上下文动态决定掩码策略

| 场景 | 掩码策略 |
|-----|---------|
| 普通用户查看 | 完全隐藏 |
| 管理员查看 | 部分显示 |
| 系统内部处理 | 不掩码 |
| 日志记录 | 完全隐藏 |

### 5.3 AI增强掩码 (AI-Enhanced Masking)

基于 pii-masker 项目的AI方法：

| 技术 | 说明 | 优势 |
|-----|------|------|
| DeBERTa-v3 | 预训练语言模型 | 高精度，上下文理解 |
| NER (命名实体识别) | 识别PII实体 | 适合复杂场景 |
| 规则+AI混合 | 正则+模型双重检测 | 兼顾准确率和召回率 |

---

## 6. 本项目实现建议

### 6.1 检测类型优先级

基于GitHub项目实践和PII-Bench研究：

| 优先级 | 检测类型 | 实现方式 |
|-------|---------|---------|
| P0 | API密钥 (OpenAI, AWS, GitHub等) | 正则匹配 |
| P0 | 密码字段 (password=, pwd=等) | 正则匹配 |
| P0 | JWT Token | 正则匹配 |
| P1 | 邮箱地址 | 正则匹配 |
| P1 | 手机号(中国) | 正则匹配 |
| P2 | 身份证号 | 正则匹配 |
| P2 | 银行卡号 | 正则匹配 |
| P3 | 私钥文件标识 | 正则匹配 |

### 6.2 掩码方案

```
API密钥: sk-proj-abc...xyz → sk-proj-****xyz (保留前缀和后3位)
邮箱: user@example.com → u***@example.com (保留首字母和域名)
手机号: 13812345678 → 138****5678 (保留前3后4位)
身份证: 110101199001011234 → 110101********1234 (保留前6后4位)
密码字段: password=admin123 → password=****** (完全隐藏)
```

### 6.3 代码实现参考

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

## 7. 安全建议

1. **最小化存储**：检测完成后尽量不保留原始敏感数据
2. **分级掩码**：根据数据敏感度选择不同掩码策略
3. **日志脱敏**：确保日志中不记录明文敏感信息
4. **传输加密**：API响应中使用掩码值，不返回原文

---

## 8. 参考资源汇总

### 学术论文
- [PII-Bench](https://arxiv.org/abs/2502.18545) - PII保护评估框架
- [PII-Scope](https://arxiv.org/abs/2410.06704) - LLM中PII泄露研究
- [SoK: Differential Privacies](https://arxiv.org/abs/1906.01337) - 差分隐私综述

### 开源项目
- [earlybird](https://github.com/americanexpress/earlybird) - 美国运通敏感数据检测工具
- [pii-masker](https://github.com/HydroXai/pii-masker) - AI驱动的PII掩码
- [safe-zone](https://github.com/thyrisAI/safe-zone) - PII护栏引擎
- [cipher-gate](https://github.com/PkLavc/cipher-gate) - 动态数据掩码网关

### 标准规范
- PCI DSS: 支付卡行业数据安全标准
- GDPR: 通用数据保护条例
- NIST SP 800-122: 个人身份信息保护指南
- OWASP Top 10: 敏感数据暴露防护
