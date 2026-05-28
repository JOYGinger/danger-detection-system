# 系统架构文档

## 1. 系统概述

危险检测集成系统是一个面向个人用户的独立安全检测工具，采用前后端分离架构，支持本地部署，保护用户隐私。

**信息安全知识点体现**：
- 数据加密存储（AES-256）
- 敏感信息掩码技术
- 最小权限原则
- 安全默认配置

---

## 2. 技术架构

```
┌─────────────────────────────────────────┐
│              Web 界面 (React)            │
│         端口: 3000                       │
└─────────────────┬───────────────────────┘
                  │ HTTPS (推荐)
┌─────────────────▼───────────────────────┐
│            API 服务 (FastAPI)            │
│         端口: 8000                       │
│  ┌─────────────────────────────────────┐│
│  │         检测引擎                     ││
│  │  ┌─────────┐ ┌─────────┐ ┌────────┐ ││
│  │  │钓鱼邮件  │ │ 弱密码   │ │敏感信息 │ ││
│  │  │TF-IDF+RF│ │ zxcvbn  │ │正则+规则│ ││
│  │  └─────────┘ └─────────┘ └────────┘ ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │      加密层 (Fernet/AES-GCM)         ││
│  │      信息安全核心：数据保密性保护      ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │         存储层 (SQLite)              ││
│  │      敏感数据加密存储                 ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

---

## 3. 目录结构

```
.
├── docker-compose.yml
├── CLAUDE.md
├── memory-bank/
│   ├── design-document.md
│   ├── tech-stack.md
│   ├── implementation-plan.md
│   ├── progress.md
│   └── architecture.md
├── research/
│   ├── phishing-detection-nlp.md
│   ├── sensitive-data-masking.md
│   ├── database-security-storage.md
│   └── password-strength-detection.md
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
│       ├── api/
│       │   ├── client.ts
│       │   ├── detection.ts
│       │   └── history.ts
│       ├── components/
│       ├── pages/
│       │   ├── DetectPage.tsx
│       │   └── HistoryPage.tsx
│       ├── store/
│       │   └── useStore.ts
│       └── main.tsx
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── crypto.py          # 加密工具类
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── detection.py       # SQLAlchemy ORM模型
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── detection.py       # Pydantic模型
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── detection.py       # API路由
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── detector.py        # 检测服务
│   │   │   └── history.py         # 历史记录服务
│   │   └── detectors/
│   │       ├── __init__.py        # 检测器工厂
│   │       ├── base.py            # 检测器基类
│   │       ├── phishing.py        # 钓鱼邮件检测
│   │       ├── weak_password.py   # 弱密码检测
│   │       └── sensitive_info.py  # 敏感信息检测
│   └── tests/
│       ├── __init__.py
│       ├── test_detectors.py
│       ├── test_api.py
│       └── test_crypto.py
└── data/
    ├── detections.db              # SQLite数据库（加密存储）
    ├── models/                    # 训练好的模型文件
    │   ├── phishing_model.joblib
    │   └── tfidf_vectorizer.joblib
    └── training/                  # 训练数据
        ├── phishing_emails.csv
        ├── normal_emails.csv
        └── phishing_keywords.json
```

---

## 4. 核心模块说明

### 4.1 前端模块

| 模块 | 路径 | 职责 |
|-----|------|------|
| API客户端 | src/api/ | 封装HTTP请求，与后端通信 |
| 组件 | src/components/ | 可复用UI组件 |
| 页面 | src/pages/ | 页面级组件（检测页、历史页） |
| 状态管理 | src/store/ | Zustand全局状态 |

### 4.2 后端模块

| 模块 | 路径 | 职责 | 信息安全知识点 |
|-----|------|------|---------------|
| 入口 | app/main.py | FastAPI应用配置 | CORS安全配置 |
| 配置 | app/config.py | 环境变量管理 | 密钥管理（不硬编码） |
| 加密工具 | app/utils/crypto.py | 数据加密解密 | **AES-256-GCM加密** |
| 数据库 | app/database.py | SQLAlchemy引擎配置 | - |
| ORM模型 | app/models/ | 数据模型定义 | 加密字段设计 |
| 模式 | app/schemas/ | Pydantic验证 | 输入验证 |
| 路由 | app/routers/ | API端点 | - |
| 服务 | app/services/ | 业务逻辑 | - |
| 检测器 | app/detectors/ | 三种检测功能 | **安全检测核心** |

### 4.3 检测器模块详解

| 检测器 | 技术方案 | 检测原理 | 信息安全知识点 |
|-------|---------|---------|---------------|
| 钓鱼邮件 | TF-IDF + RandomForest | NLP文本分类 | **社会工程学识别** |
| 弱密码 | zxcvbn-python | 熵值计算+模式匹配 | **密码学基础** |
| 敏感信息 | 正则+规则引擎 | 模式匹配+启发式规则 | **数据泄露防护(DLP)** |

---

## 5. 数据流

```
用户输入 → 前端组件 → API客户端 → 后端路由 → 检测服务 → 检测器
                                                      ↓
                           数据库 ← 加密存储 ← 历史服务 ← 结果
                           (密文)    (Fernet)
```

**信息安全要点**：
1. 传输层：建议HTTPS
2. 处理层：敏感数据仅在内存中处理
3. 存储层：敏感字段AES加密

---

## 6. API端点

| 方法 | 路径 | 描述 | 安全措施 |
|-----|------|------|---------|
| POST | /api/detect/text | 文本内容检测 | 输入验证 |
| GET | /api/history | 获取检测历史 | 分页限制 |
| GET | /api/history/{id} | 获取单条记录 | - |
| DELETE | /api/history/{id} | 删除单条记录 | - |
| DELETE | /api/history | 清空所有历史 | 确认机制 |
| GET | /health | 健康检查 | - |

---

## 7. 检测器接口

所有检测器遵循统一接口：

```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class DetectionResult:
    type: str           # 检测类型: phishing/weak_password/sensitive_info
    risk_level: str     # 风险等级: high/medium/low/safe
    confidence: float   # 置信度 (0-1)
    details: Dict       # 详细结果（各检测器不同）
    suggestions: List[str]  # 安全建议

class BaseDetector:
    def detect(self, content: str) -> DetectionResult:
        """检测入口，子类实现"""
        raise NotImplementedError
```

---

## 8. 加密存储设计

### 8.1 加密方案

| 字段 | 加密算法 | 密钥来源 |
|-----|---------|---------|
| input_content | Fernet (AES-128-CBC + HMAC-SHA256) | 环境变量 |
| result_detail | Fernet (AES-128-CBC + HMAC-SHA256) | 环境变量 |

### 8.2 密钥管理

```
应用启动 → 读取 ENCRYPTION_KEY 环境变量
         ↓
    未设置 → 报错退出（安全默认）
         ↓
    已设置 → 初始化加密器 → 正常运行
```

**信息安全原则**：
- 密钥不硬编码
- 密钥不提交到版本控制
- 启动时验证密钥存在

---

## 9. 更新日志

### 2026-05-28
- 更新技术选型：zxcvbn-python替代自实现
- 更新检测方案：敏感信息检测采用正则+规则引擎
- 更新目录结构：添加utils/、data/models/、data/training/
- 添加信息安全知识点说明
- 明确加密存储设计方案
- 添加密钥管理安全要求

### 2026-05-21
- 初始架构设计
- 确定三大检测功能：钓鱼邮件（NLP）、弱密码、敏感信息泄露
