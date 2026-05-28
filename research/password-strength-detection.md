# 弱密码检测技术 - 研究总结

## 1. 概述

本文档总结密码强度检测的核心原理和方法，参考zxcvbn的设计思路，为本项目的简化版弱密码检测器提供实现参考。

---

## 2. zxcvbn 核心原理

### 2.1 评分体系

zxcvbn使用0-4的评分系统：

| 评分 | 强度 | 熵值(bits) | 破解时间 | 说明 |
|-----|------|-----------|---------|------|
| 0 | 很弱 | < 28 | < 1秒 | 极易被破解 |
| 1 | 弱 | 28-35 | < 1分钟 | 常见密码 |
| 2 | 一般 | 36-59 | < 1天 | 需要加强 |
| 3 | 强 | 60-127 | < 1年 | 可接受 |
| 4 | 很强 | ≥ 128 | > 1年 | 推荐 |

### 2.2 检测维度

zxcvbn从以下维度分析密码：

| 维度 | 检测内容 | 示例 |
|-----|---------|------|
| 字典匹配 | 常见密码字典 | password, 123456 |
| 键盘模式 | 键盘连续按键 | qwerty, asdfgh |
| 日期模式 | 日期格式 | 19900101, 20240101 |
| 重复模式 | 重复字符 | aaa, 111, abcabc |
| 序列模式 | 递增递减序列 | abc, 123, cba |
| 组合模式 | 多模式组合 | password123 |

### 2.3 熵值计算

**公式**：
```
熵值 = log2(可能组合数)

简化计算：
- 仅小写字母: len × log2(26) ≈ len × 4.7
- 大小写混合: len × log2(52) ≈ len × 5.7
- 加数字: len × log2(62) ≈ len × 5.95
- 加符号: len × log2(95) ≈ len × 6.6
```

---

## 3. 简化版检测器设计

### 3.1 检测规则

#### 规则1：长度检查

| 长度 | 评分 | 说明 |
|-----|------|------|
| < 6 | -2 | 太短 |
| 6-7 | -1 | 较短 |
| 8-11 | 0 | 基本合格 |
| 12-15 | +1 | 较好 |
| ≥ 16 | +2 | 很好 |

#### 规则2：字符类型检查

| 字符类型 | 正则模式 | 评分 |
|---------|---------|------|
| 小写字母 | `[a-z]` | +0 (基础) |
| 大写字母 | `[A-Z]` | +1 |
| 数字 | `[0-9]` | +1 |
| 特殊符号 | `[!@#$%^&*()_+\-=\[\]{}|;':",./<>?]` | +2 |

#### 规则3：常见弱密码黑名单

```
top_100_passwords = [
    "password", "123456", "12345678", "qwerty", "abc123",
    "monkey", "1234567", "letmein", "trustno1", "dragon",
    "baseball", "iloveyou", "master", "sunshine", "ashley",
    "bailey", "passw0rd", "shadow", "123123", "654321",
    "superman", "qazwsx", "michael", "football", "password1",
    # ... 可扩展
]
```

#### 规则4：模式检测

| 模式 | 正则 | 扣分 |
|-----|------|------|
| 纯数字 | `^\d+$` | -2 |
| 纯字母 | `^[a-zA-Z]+$` | -1 |
| 键盘序列 | `qwerty|asdf|zxcv|12345|54321` | -2 |
| 重复字符 | `(.)\1{2,}` | -1 |
| 连续序列 | `abc|bcd|cde|123|234|345` | -1 |

#### 规则5：个人信息关联（可选）

| 检测项 | 说明 |
|-------|------|
| 用户名 | 密码包含用户名 |
| 日期 | 密码包含生日格式 |
| 常见词 | 密码是英文常见词汇 |

### 3.2 评分计算

```python
def calculate_score(password: str) -> int:
    score = 0
    
    # 长度评分
    if len(password) < 6:
        score -= 2
    elif len(password) < 8:
        score -= 1
    elif len(password) >= 12:
        score += 1
    elif len(password) >= 16:
        score += 2
    
    # 字符类型评分
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{}|;\'",./<>?]', password))
    
    score += sum([has_upper, has_digit, has_special * 2])
    
    # 弱密码黑名单
    if password.lower() in top_100_passwords:
        score -= 3
    
    # 模式扣分
    if re.match(r'^\d+$', password):
        score -= 2
    if re.search(r'qwerty|asdf|12345', password.lower()):
        score -= 2
    
    # 归一化到0-4
    return max(0, min(4, score))
```

### 3.3 熵值简化计算

```python
def calculate_entropy(password: str) -> float:
    """简化熵值计算"""
    charset_size = 0
    
    if re.search(r'[a-z]', password):
        charset_size += 26
    if re.search(r'[A-Z]', password):
        charset_size += 26
    if re.search(r'[0-9]', password):
        charset_size += 10
    if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;\'",./<>?]', password):
        charset_size += 32  # 常见特殊字符
    
    if charset_size == 0:
        return 0
    
    import math
    return len(password) * math.log2(charset_size)
```

---

## 4. 风险等级映射

| 评分 | 熵值(bits) | 风险等级 | 用户反馈 |
|-----|-----------|---------|---------|
| 0 | < 28 | 高 | "密码太弱，极易被破解" |
| 1 | 28-35 | 高 | "密码较弱，建议增加复杂度" |
| 2 | 36-59 | 中 | "密码一般，建议加强" |
| 3 | 60-127 | 低 | "密码强度良好" |
| 4 | ≥ 128 | 低 | "密码强度很高" |

---

## 5. 建议生成

根据检测结果生成个性化建议：

```python
def generate_suggestions(password: str, score: int) -> list:
    suggestions = []
    
    if len(password) < 8:
        suggestions.append("使用至少8位密码")
    if not re.search(r'[A-Z]', password):
        suggestions.append("添加大写字母")
    if not re.search(r'[0-9]', password):
        suggestions.append("添加数字")
    if not re.search(r'[!@#$%^&*]', password):
        suggestions.append("添加特殊字符")
    if re.match(r'^\d+$', password):
        suggestions.append("不要使用纯数字")
    if re.search(r'qwerty|asdf|12345', password.lower()):
        suggestions.append("避免使用键盘连续按键")
    
    if score >= 3:
        suggestions.append("密码强度良好，请妥善保管")
    
    return suggestions[:5]  # 最多返回5条建议
```

---

## 6. 实现注意事项

1. **不要存储用户输入的密码**：仅计算强度并返回结果
2. **结果不保存原文**：历史记录中仅保存风险等级和评分
3. **内存中处理**：处理完成后立即清除密码变量
4. **前端传输**：使用HTTPS确保传输安全

---

## 7. 参考资源

- zxcvbn源码: https://github.com/dropbox/zxcvbn
- NIST SP 800-63B: 数字身份指南（密码部分）
- OWASP Password Strength Cheat Sheet
- 常见密码列表: https://github.com/danielmiessler/SecLists
