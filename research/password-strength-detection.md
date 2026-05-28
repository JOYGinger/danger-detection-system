# 弱密码检测技术 - 研究总结

## 1. 概述

本文档总结密码强度检测的核心原理和方法，参考zxcvbn的设计思路和最新学术研究，为本项目的简化版弱密码检测器提供实现参考。

---

## 2. 学术论文资源（arXiv）

### 2.1 密码强度评估研究

| 论文标题 | 年份 | 链接 | 核心贡献 |
|---------|------|------|---------|
| Adversarial Machine Learning for Robust Password Strength Estimation | 2025 | [arXiv:2506.00373](https://arxiv.org/abs/2506.00373) | 对抗训练提升20%准确率，67万对抗样本 |
| Interpretable Probabilistic Password Strength Meters via Deep Learning | 2020 | [arXiv:2004.07179](https://arxiv.org/abs/2004.07179) | 可解释概率模型，字符级安全贡献分析 |
| Expectation Entropy as a Password Strength Metric | 2024 | [arXiv:2404.16853](https://arxiv.org/abs/2404.16853) | 期望熵新指标，0-1范围标准化 |
| A Canonical Password Strength Measure | 2015 | [arXiv:1505.05090](https://arxiv.org/abs/1505.05090) | 密码强度规范化定义，考虑攻击者策略 |
| Passwords: Divided they Stand, United they Fall | 2020 | [arXiv:2009.03062](https://arxiv.org/abs/2009.03062) | 空间分区攻击模型，密码密度分析 |
| Password Strength Signaling: A Counter-Intuitive Defense | 2020 | [arXiv:2009.10060](https://arxiv.org/abs/2009.10060) | 密码强度信号防御，减少12%破解率 |

### 2.2 关键技术发现

**对抗训练方法 (2025)：**
- 使用故意设计的欺骗性密码训练
- 对抗训练提升分类准确率20%
- 5种分类算法对比验证
- 67万+对抗样本数据集

**可解释密码强度计 (2020)：**
- 每个字符的安全贡献可视化
- 无人工偏见的反馈
- 概率解释的强度建议
- 轻量级深度学习框架，支持客户端运行

**期望熵指标 (2024)：**
- 结果在0-1范围，便于理解
- 例如0.4表示攻击者需搜索40%空间
- 适用于随机或类随机密码

---

## 3. GitHub开源项目

### 3.1 zxcvbn系列（核心参考）

| 项目名称 | Stars | 链接 | 技术栈 | 说明 |
|---------|-------|------|--------|------|
| **zxcvbn** (Dropbox官方) | 15,968 | [GitHub](https://github.com/dropbox/zxcvbn) | CoffeeScript/JS | 原版实现，低预算密码强度估算 |
| **zxcvbn-ts** | 1,175 | [GitHub](https://github.com/zxcvbn-ts/zxcvbn) | TypeScript | TypeScript版本，前端友好 |
| **zxcvbn-python** | 714 | [GitHub](https://github.com/dwolfhub/zxcvbn-python) | Python | Python实现，本项目推荐 |
| **zxcvbn-php** | 870 | [GitHub](https://github.com/bjeavons/zxcvbn-php) | PHP | PHP移植版 |
| **zxcvbn-go** | 393 | [GitHub](https://github.com/nbutton23/zxcvbn-go) | Go | Go语言实现 |
| **zxcvbn4j** | 362 | [GitHub](https://github.com/nulab/zxcvbn4j) | Java | Java移植版 |
| **zxcvbn-rs** | 261 | [GitHub](https://github.com/shssoichiro/zxcvbn-rs) | Rust | Rust实现 |

### 3.2 zxcvbn核心原理

**评分体系**：

| 评分 | 强度 | 熵值(bits) | 破解时间 | 说明 |
|-----|------|-----------|---------|------|
| 0 | 很弱 | < 28 | < 1秒 | 极易被破解 |
| 1 | 弱 | 28-35 | < 1分钟 | 常见密码 |
| 2 | 一般 | 36-59 | < 1天 | 需要加强 |
| 3 | 强 | 60-127 | < 1年 | 可接受 |
| 4 | 很强 | ≥ 128 | > 1年 | 推荐 |

**检测维度**：

| 维度 | 检测内容 | 示例 |
|-----|---------|------|
| 字典匹配 | 常见密码字典 | password, 123456 |
| 键盘模式 | 键盘连续按键 | qwerty, asdfgh |
| 日期模式 | 日期格式 | 19900101, 20240101 |
| 重复模式 | 重复字符 | aaa, 111, abcabc |
| 序列模式 | 递增递减序列 | abc, 123, cba |
| 组合模式 | 多模式组合 | password123 |

---

## 4. 简化版检测器设计

### 4.1 检测规则

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

```python
# 来源: SecLists 常见密码列表
top_100_passwords = [
    "password", "123456", "12345678", "qwerty", "abc123",
    "monkey", "1234567", "letmein", "trustno1", "dragon",
    "baseball", "iloveyou", "master", "sunshine", "ashley",
    "bailey", "passw0rd", "shadow", "123123", "654321",
    "superman", "qazwsx", "michael", "football", "password1",
    # ... 参考 SecLists 扩展
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

### 4.2 评分计算

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

### 4.3 熵值计算

```python
import math

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
    
    return len(password) * math.log2(charset_size)
```

---

## 5. 风险等级映射

| 评分 | 熵值(bits) | 风险等级 | 用户反馈 |
|-----|-----------|---------|---------|
| 0 | < 28 | 高 | "密码太弱，极易被破解" |
| 1 | 28-35 | 高 | "密码较弱，建议增加复杂度" |
| 2 | 36-59 | 中 | "密码一般，建议加强" |
| 3 | 60-127 | 低 | "密码强度良好" |
| 4 | ≥ 128 | 低 | "密码强度很高" |

---

## 6. 建议生成

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

## 7. 实现注意事项

1. **加密保存输入内容**：根据用户确认，密码检测结果需加密保存输入内容
2. **结果不保存原文**：历史记录中保存加密后的输入内容和评分结果
3. **内存中处理**：处理完成后立即清除密码变量
4. **前端传输**：使用HTTPS确保传输安全

---

## 8. 参考资源汇总

### 学术论文
- [Adversarial ML for Password Strength](https://arxiv.org/abs/2506.00373) - 对抗训练方法
- [Interpretable Password Meters](https://arxiv.org/abs/2004.07179) - 可解释深度学习
- [Expectation Entropy](https://arxiv.org/abs/2404.16853) - 新型熵值指标
- [Canonical Password Strength](https://arxiv.org/abs/1505.05090) - 强度规范化定义

### 开源项目
- [zxcvbn (Dropbox)](https://github.com/dropbox/zxcvbn) - 原版实现，15968 stars
- [zxcvbn-python](https://github.com/dwolfhub/zxcvbn-python) - Python版本推荐
- [SecLists](https://github.com/danielmiessler/SecLists) - 常见密码列表

### 标准规范
- NIST SP 800-63B: 数字身份指南（密码部分）
- OWASP Password Strength Cheat Sheet
