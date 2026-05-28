# 钓鱼邮件检测 - NLP与机器学习研究总结

## 1. 研究背景

AI生成的钓鱼邮件越来越难以识别，传统的基于规则和黑名单的方法已不足以应对。基于NLP和机器学习的方法成为主流研究方向。

---

## 2. 学术论文资源（arXiv）

### 2.1 最新研究论文

| 论文标题 | 年份 | 链接 | 核心贡献 |
|---------|------|------|---------|
| Phishsense-1B: A Technical Perspective on an AI-Powered Phishing Detection Model | 2025 | [arXiv:2503.10944](https://arxiv.org/abs/2503.10944) | 基于Llama-Guard-3-1B微调，使用LoRA和GuardReasoner方法，达到97.5%准确率 |
| PhishDebate: An LLM-Based Multi-Agent Framework for Phishing Website Detection | 2025 | [arXiv:2506.15656](https://arxiv.org/abs/2506.15656) | 多Agent辩论框架，98.2%召回率，模块化设计 |
| Novel Interpretable and Robust Web-based AI Platform for Phishing Email Detection | 2024 | [arXiv:2405.11619](https://arxiv.org/abs/2405.11619) | F1分数0.99，集成可解释AI(XAI)，提供Web应用 |
| A Deep Learning Model with Hierarchical LSTMs and Supervised Attention for Anti-Phishing | 2018 | [arXiv:1805.01554](https://arxiv.org/abs/1805.01554) | 层次LSTM+注意力机制，词级和句级双重建模 |
| Analyzing Social and Stylometric Features to Identify Spear phishing Emails | 2014 | [arXiv:1406.3692](https://arxiv.org/abs/1406.3692) | 社交特征+风格计量特征，97.76%准确率 |

### 2.2 关键技术要点

**Phishsense-1B (2025) 关键发现：**
- 使用LoRA微调大语言模型效果显著
- 在自定义数据集上达到97.5%准确率
- 在真实世界数据集上保持70%准确率
- 明显超越BERT-based检测器

**PhishDebate (2025) 多Agent框架：**
- 四个专业Agent：URL结构、HTML组成、语义内容、品牌冒充
- Moderator协调 + Judge最终决策
- 结构化辩论机制，降低幻觉问题
- 模块化设计，支持按需配置

**H-LSTM + Attention (2018) 方案：**
- 词级LSTM捕获局部特征
- 句级LSTM捕获全局结构
- 监督注意力聚焦关键部分

---

## 3. GitHub开源项目

### 3.1 钓鱼网站检测项目

| 项目名称 | Stars | 链接 | 技术栈 | 说明 |
|---------|-------|------|--------|------|
| Phishing-Website-Detection-by-Machine-Learning-Techniques | 401 | [GitHub](https://github.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques) | Jupyter Notebook | 多种ML技术对比 |
| Malicious-Web-Content-Detection-Using-Machine-Learning | 256 | [GitHub](https://github.com/philomathic-guy/Malicious-Web-Content-Detection-Using-Machine-Learning) | Python | Chrome扩展，实时检测 |
| Phishing-Website-Detection | 195 | [GitHub](https://github.com/chamanthmvs/Phishing-Website-Detection) | Jupyter Notebook | Python ML实现 |
| WhiteHat | 114 | [GitHub](https://github.com/urcuqui/WhiteHat) | Jupyter Notebook | AI安全工具集，含钓鱼检测、对抗ML |
| phishing-website-detection-content-based | 33 | [GitHub](https://github.com/emre-kocyigit/phishing-website-detection-content-based) | Python | 基于HTML内容特征 |

### 3.2 钓鱼邮件检测项目（NLP重点）

| 项目名称 | Stars | 链接 | 技术栈 | 说明 |
|---------|-------|------|--------|------|
| Email-Phishing-Attempts-Detection-using-NLP | 28 | [GitHub](https://github.com/mo-messidi/Email-Phishing-Attempts-Detection-using-NLP) | Jupyter Notebook | NLP+ML邮件检测 |
| Phishing-Email-Detection-Using-Machine-Learning | 32 | [GitHub](https://github.com/Click2Hack/Phishing-Email-Detection-Using-Machine-Learning) | Python | 邮件文本检测 |
| AI-Powered-Phishing-Detection-System | 8 | [GitHub](https://github.com/GauravGhandat-23/AI-Powered-Phishing-Detection-System) | Python | ML+NLP，检测邮件正文和URL |
| Ai-Phishing-Detector | 4 | [GitHub](https://github.com/credkellar-boop/Ai-Phishing-Detector) | Python | TF-IDF + Random Forest |
| PhishGuardian | 2 | [GitHub](https://github.com/r4nol/PhishGuardian) | Jupyter Notebook | 微调DistilBERT |

---

## 4. 核心技术方法

### 4.1 特征提取方法

| 特征类型 | 具体特征 | 说明 |
|---------|---------|------|
| **词汇特征** | TF-IDF、词频统计 | 统计钓鱼邮件高频词汇 |
| **语义特征** | 词向量(Word2Vec)、BERT嵌入 | 捕获语义信息 |
| **结构特征** | 邮件头部、链接数量、HTML标签 | 邮件结构分析 |
| **情感特征** | 紧迫性词汇、威胁性语言 | 社会工程学特征 |

### 4.2 推荐模型架构

```
文本输入 → 中文分词(jieba) → 特征提取(TF-IDF/词向量) → 机器学习模型 → 风险分类
```

**推荐模型选择**（按复杂度排序）：

1. **朴素贝叶斯 (Naive Bayes)** - 简单高效，适合MVP
2. **支持向量机 (SVM)** - 文本分类效果好
3. **随机森林 (Random Forest)** - 可解释性强，推荐使用
4. **XGBoost/LightGBM** - 性能优秀
5. **DistilBERT/LLM微调** - 最高准确率，需要更多资源

### 4.3 中文钓鱼词汇特征

```python
# 紧迫性词汇
urgency_words = ["立即", "紧急", "马上", "尽快", "限时", "最后机会", "今日截止", "即将过期"]

# 威胁性词汇
threat_words = ["冻结", "封禁", "异常", "风险", "安全", "验证", "锁定", "暂停", "停止服务"]

# 诱导性词汇
lure_words = ["点击", "链接", "验证身份", "确认信息", "领取奖励", "免费", "优惠", "中奖"]

# 伪装性词汇
disguise_words = ["官方", "客服", "银行", "支付宝", "微信支付", "淘宝", "京东", "税务局", "公安局"]
```

---

## 5. 本项目实现建议

### 5.1 MVP阶段方案

基于研究发现，推荐使用以下技术栈：

| 组件 | 选择 | 理由 |
|-----|------|------|
| 分词工具 | jieba | 中文分词标准选择 |
| 特征提取 | TF-IDF | 简单有效 |
| 分类模型 | RandomForest | 可解释性强，无需GPU |
| 训练数据 | 100+100样本 | 参考GitHub项目实践 |

### 5.2 模型评估指标

- **准确率 (Accuracy)**：整体分类正确率
- **精确率 (Precision)**：预测为钓鱼邮件中实际是钓鱼邮件的比例
- **召回率 (Recall)**：实际钓鱼邮件中被正确识别的比例
- **F1-Score**：精确率和召回率的调和平均

### 5.3 进阶方案（可选）

| 升级方向 | 技术选择 | 预期收益 |
|---------|---------|---------|
| 预训练模型 | DistilBERT中文 | 准确率提升10-15% |
| 大模型微调 | Llama-Phishsense | 准确率可达97%+ |
| 多Agent框架 | PhishDebate架构 | 可解释性增强 |

---

## 6. 数据集资源

| 数据集名称 | 链接 | 说明 |
|-----------|------|------|
| Phishing Email Dataset (Kaggle) | [Kaggle](https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset/) | 论文引用，最大公开数据集 |
| Phishtank | [phishtank.org](https://www.phishtank.org/) | 实时钓鱼URL数据库 |
| APWG | [apwg.org](https://apwg.org/) | 反钓鱼工作组数据 |

---

## 7. 参考资源汇总

### 学术论文
- [Phishsense-1B](https://arxiv.org/abs/2503.10944) - LLM微调，97.5%准确率
- [PhishDebate](https://arxiv.org/abs/2506.15656) - 多Agent辩论框架
- [Novel Interpretable AI Platform](https://arxiv.org/abs/2405.11619) - 可解释AI，F1=0.99
- [H-LSTM for Anti-Phishing](https://arxiv.org/abs/1805.01554) - 层次LSTM方法

### 开源项目
- [Email-Phishing-NLP](https://github.com/mo-messidi/Email-Phishing-Attempts-Detection-using-NLP) - NLP邮件检测
- [Ai-Phishing-Detector](https://github.com/credkellar-boop/Ai-Phishing-Detector) - TF-IDF + RF实现
- [PhishGuardian](https://github.com/r4nol/PhishGuardian) - DistilBERT微调

### 工具库
- scikit-learn 文档: https://scikit-learn.org/stable/modules/feature_extraction.html
- jieba 中文分词: https://github.com/fxsjy/jieba
- HuggingFace Transformers: https://huggingface.co/models
