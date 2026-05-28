# 系统架构文档

## 1. 系统概述

危险检测集成系统是一个面向个人用户的独立安全检测工具，采用前后端分离架构，支持本地部署，保护用户隐私。

---

## 2. 技术架构

```
┌─────────────────────────────────────────┐
│              Web 界面 (React)            │
│         端口: 3000                       │
└─────────────────┬───────────────────────┘
                  │ HTTP API
┌─────────────────▼───────────────────────┐
│            API 服务 (FastAPI)            │
│         端口: 8000                       │
│  ┌─────────────────────────────────────┐│
│  │         检测引擎                     ││
│  │  ┌─────────┐ ┌─────────┐ ┌────────┐ ││
│  │  │钓鱼邮件  │ │ 弱密码   │ │敏感信息 │ ││
│  │  │ 检测器   │ │ 检测器   │ │ 检测器 │ ││
│  │  └─────────┘ └─────────┘ └────────┘ ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │         存储层 (SQLite)              ││
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
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
│       ├── api/
│       ├── components/
│       ├── pages/
│       ├── store/
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
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── detection.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── detection.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── detection.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── detector.py
│   │   │   └── history.py
│   │   └── detectors/
│   │       ├── __init__.py
│   │       ├── phishing.py
│   │       ├── weak_password.py
│   │       └── sensitive_info.py
│   └── tests/
│       ├── __init__.py
│       └── test_detectors.py
└── data/
    └── detections.db
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

| 模块 | 路径 | 职责 |
|-----|------|------|
| 入口 | app/main.py | FastAPI应用配置、路由注册 |
| 数据库 | app/database.py | SQLAlchemy引擎配置 |
| 模型 | app/models/ | ORM模型定义 |
| 模式 | app/schemas/ | Pydantic请求/响应模型 |
| 路由 | app/routers/ | API端点定义 |
| 服务 | app/services/ | 业务逻辑封装 |
| 检测器 | app/detectors/ | 三种检测功能实现 |

---

## 5. 数据流

```
用户输入 → 前端组件 → API客户端 → 后端路由 → 检测服务 → 检测器
                                                      ↓
数据库 ← 历史服务 ← 结果 ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

---

## 6. API端点

| 方法 | 路径 | 描述 |
|-----|------|------|
| POST | /api/detect/text | 文本内容检测 |
| GET | /api/history | 获取检测历史 |
| DELETE | /api/history/{id} | 删除单条历史 |
| DELETE | /api/history | 清空所有历史 |
| GET | /health | 健康检查 |

---

## 7. 检测器接口

所有检测器遵循统一接口：

```python
class DetectorResult:
    type: str           # 检测类型
    risk_level: str     # 风险等级: high/medium/low/safe
    details: dict       # 详细结果（各检测器不同）

def detect(content: str) -> DetectorResult
```

---

## 8. 更新日志

### 2026-05-21
- 初始架构设计
- 确定三大检测功能：钓鱼邮件（NLP）、弱密码、敏感信息泄露
