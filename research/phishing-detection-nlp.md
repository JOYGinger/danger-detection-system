# 钓鱼邮件检测 - NLP与机器学习研究总结

## 1. 研究背景

AI生成的钓鱼邮件越来越难以识别，传统的基于规则和黑名单的方法已不足以应对。基于NLP和机器学习的方法成为主流研究方向。

---

## 2. 相关研究论文

### 2.1 经典论文

| 论文标题 | 年份 | 核心贡献 |
|---------|------|---------|
| "Phishing Detection Using Machine Learning Techniques" | 2019 | 对比了多种机器学习算法在钓鱼邮件检测中的表现 |
| "Natural Language Processing Based Phishing Email Detection" | 2020 | 提出基于NLP特征的钓鱼邮件检测框架 |
| "Deep Learning for Phishing Email Detection" | 2021 | 使用LSTM和CNN处理邮件文本序列 |
| "BERT-based Phishing Email Detection" | 2022 | 预训练语言模型在钓鱼邮件检测中的应用 |

### 2.2 推荐阅读

- **Ram Basnet et al.** "Detection of Phishing Emails: A Machine Learning Approach" - 详细的特征工程方法
- **Fang Yu et al.** "PhishIntention: Detecting Phishing Intention via Webpage Appearance" - 意图检测方法
- ** Sahar Abdel-Gaber et al.** "Phishing Email Detection Using NLP and Machine Learning" - NLP特征提取方法

---

## 3. 核心技术方法

### 3.1 特征提取方法

| 特征类型 | 具体特征 | 说明 |
|---------|---------|------|
| **词汇特征** | TF-IDF、词频统计 | 统计钓鱼邮件高频词汇 |
| **语义特征** | 词向量(Word2Vec)、BERT嵌入 | 捕获语义信息 |
| **结构特征** | 邮件头部、链接数量、HTML标签 | 邮件结构分析 |
| **情感特征** | 紧迫性词汇、威胁性语言 | 社会工程学特征 |

### 3.2 推荐模型架构

```
文本输入 → 中文分词(jieba) → 特征提取(TF-IDF/词向量) → 机器学习模型 → 风险分类
```

**推荐模型选择**（按复杂度排序）：

1. **朴素贝叶斯 (Naive Bayes)** - 简单高效，适合MVP
2. **支持向量机 (SVM)** - 文本分类效果好
3. **随机森林 (Random Forest)** - 可解释性强
4. **XGBoost/LightGBM** - 性能优秀

### 3.3 特征工程重点

对于中文钓鱼邮件检测，重点关注：

```python
# 紧迫性词汇
urgency_words = ["立即", "紧急", "马上", "尽快", "限时", "最后机会"]

# 威胁性词汇
threat_words = ["冻结", "封禁", "异常", "风险", "安全", "验证"]

# 诱导性词汇
lure_words = ["点击", "链接", "验证身份", "确认信息", "领取奖励"]

# 社会工程学特征
se_features = ["官方", "客服", "银行", "支付宝", "微信支付"]
```

---

## 4. 实现建议

### 4.1 MVP阶段

1. 使用 **TF-IDF + 朴素贝叶斯/随机森林** 组合
2. 手工标注100-200条中文钓鱼邮件样本
3. 重点提取紧迫性、威胁性词汇特征

### 4.2 数据集构建

| 数据来源 | 说明 |
|---------|------|
| 公开数据集 | Kaggle Phishing Email Dataset |
| 自建数据集 | 收集中文钓鱼邮件样本进行标注 |
| 数据增强 | 同义词替换、回译等方法扩充数据 |

### 4.3 模型评估指标

- **准确率 (Accuracy)**：整体分类正确率
- **精确率 (Precision)**：预测为钓鱼邮件中实际是钓鱼邮件的比例
- **召回率 (Recall)**：实际钓鱼邮件中被正确识别的比例
- **F1-Score**：精确率和召回率的调和平均

---

## 5. 参考资源

- Kaggle Phishing Email Dataset: https://www.kaggle.com/datasets
- scikit-learn 文档: https://scikit-learn.org/stable/modules/feature_extraction.html
- jieba 中文分词: https://github.com/fxsjy/jieba
