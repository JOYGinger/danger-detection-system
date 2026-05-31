# 系统架构文档

## 1. 系统概述

危险检测集成系统是一个面向个人用户的独立安全检测工具，采用前后端分离架构，支持本地部署，保护用户隐私。

**信息安全知识点体现**：
- 数据加密存储（AES-256）
- 敏感信息掩码技术
- 最小权限原则
- 安全默认配置

### 开发环境配置（重要）

本项目在WSL（Linux）和Windows双环境下开发。由于WSL创建的 `.venv` 无法在Windows主机使用，切换环境时必须重建虚拟环境：

**Windows环境首次启动步骤**：
1. `cd E:\code\security-project\claude-test\backend`
2. `Remove-Item -Recurse -Force .venv`（删除WSL创建的.venv，PowerShell语法；CMD下用 `rmdir /s /q .venv`）
3. `python -m venv .venv`
4. `.venv\Scripts\activate`
5. `pip install -r requirements.txt`
6. `python -m uvicorn app.main:app --reload`

**WSL环境同理**：删除Windows的 `.venv` 后重建。

**关键文件说明**：
- `.env`（需手动创建，从 `.env.example` 复制）：包含 `ENCRYPTION_KEY`，不可提交到版本控制
- `data/` 目录：由 `init_db()` 自动创建，存放 `detections.db`

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

### 3.1 文件作用说明

**后端核心文件**：

| 文件 | 作用 |
|-----|------|
| `backend/requirements.txt` | Python依赖清单，锁定版本确保环境一致性 |
| `backend/.env.example` | 环境变量模板，包含ENCRYPTION_KEY和DATABASE_URL |
| `backend/app/__init__.py` | Python包初始化 |
| `backend/app/main.py` | FastAPI应用入口：创建app实例（中文标题"危险检测集成系统"）；CORS中间件仅允许settings.CORS_ORIGINS中的源（默认localhost:3000）；`/health`端点返回`{"status":"ok"}`；自动生成`/docs`Swagger文档和`/openapi.json`；lifespan启动事件调用init_db()自动创建表；后续步骤在此注册路由 |
| `backend/app/config.py` | Settings配置类：从.env/环境变量读取ENCRYPTION_KEY、DATABASE_URL（默认sqlite:///./data/detections.db）、APP_ENV、DEBUG、CORS_ORIGINS（逗号分隔）；使用python-dotenv加载.env文件 |
| `backend/app/database.py` | SQLAlchemy配置：engine（SQLite，check_same_thread=False）、SessionLocal会话工厂、Base声明基类（所有ORM模型继承）、`init_db()`自动创建data目录和表结构、`get_db()`FastAPI依赖注入生成器 |
| `backend/app/utils/__init__.py` | 工具包初始化 |
| `backend/app/utils/crypto.py` | DataEncryptor类：Fernet(AES-128-CBC+HMAC-SHA256)认证加密；`encrypt(plaintext)->str`返回base64密文，空串直接返回空；`decrypt(ciphertext)->str`解密，空串直接返回空；`generate_key()->str`生成新Fernet密钥；ENCRYPTION_KEY未设置时抛出ValueError；加密在服务层手动调用，不在ORM层自动触发 |
| `backend/app/models/__init__.py` | 导出DetectionHistory模型，确保init_db()能发现模型建表 |
| `backend/app/models/detection.py` | DetectionHistory ORM模型：id(主键自增)、input_content_encrypted(Text非空，Fernet加密存储)、detection_type(String50，phishing/weak_password/sensitive_info/all)、risk_level(String20，high/medium/low/safe)、result_detail_encrypted(Text可空，Fernet加密JSON)、created_at(DateTime默认UTC)；索引idx_created_at和idx_detection_type；加密在服务层手动调用 |
| `backend/app/schemas/__init__.py` | 导出所有Pydantic模型 |
| `backend/app/schemas/detection.py` | Pydantic模型：DetectionType枚举(phishing/weak_password/sensitive_info)、RiskLevel枚举(high/medium/low/safe)、DetectRequest(content必填min_length=1，detection_type可选)、DetectResponse(success+result单类型/results全类型)、HistoryItem(不含敏感input_content，from_attributes=True)、HistoryList(items+分页)、HistoryDetail(含解密后input_content和result_detail) |
| `backend/app/routers/__init__.py` | 路由包初始化 |
| `backend/app/routers/detection.py` | API端点：POST /api/detect/text（检测后自动调用save_history加密保存记录；单类型保存实际type，全类型保存type="all"并取最高risk_level）；GET /api/history（分页列表，不含input_content，最小化数据暴露）；GET /api/history/{id}（解密后返回详情，不存在404）；DELETE /api/history/{id}（单条删除，不存在404）；DELETE /api/history（清空返回deleted_count） |
| `backend/app/services/__init__.py` | 服务包初始化 |
| `backend/app/services/detector.py` | 检测服务编排：接收请求→调用检测器→保存历史 |
| `backend/app/services/history.py` | 历史记录服务：save_history(加密存储input_content和result_detail)、get_history_list(分页，按created_at降序，不含敏感字段)、get_history_detail(解密后返回详情)、delete_history(单条删除)、clear_history(清空返回删除数)；DataEncryptor延迟初始化_get_encryptor()避免导入时环境变量未设置报错 |
| `backend/app/detectors/__init__.py` | 检测器工厂：`get_detector(type)->BaseDetector`、`detect_all(content)->Dict[str,DetectionResult]`；当前仅注册sensitive_info，后续添加phishing/weak_password时在此注册 |
| `backend/app/detectors/base.py` | DetectionResult数据类(type/risk_level/confidence/details/suggestions)、BaseDetector抽象基类(detect方法) |
| `backend/app/detectors/phishing.py` | 钓鱼邮件检测器（TF-IDF + RandomForest）— 待实现 |
| `backend/app/detectors/weak_password.py` | 弱密码检测器（zxcvbn-python）— 待实现 |
| `backend/app/detectors/sensitive_info.py` | 敏感信息检测器：11条正则规则(API密钥5种/JWT/密码/邮箱/手机/身份证/私钥)；6种掩码方式(api_key保留前7后3/email保留首字母+域名/phone前3后4/id_card前6后4/password完全隐藏/token前6位/key_file标识)；风险计算(high>medium>low)；针对性安全建议生成 |
| `backend/tests/__init__.py` | 测试包初始化 |
| `backend/tests/test_crypto.py` | 加密工具单元测试（11个用例）：加解密往返、空字符串、中文、长文本、特殊字符、不同加密产生不同密文、密钥缺失ValueError、无效密文InvalidToken、密钥生成格式和唯一性 |
| `backend/pyproject.toml` | pytest配置文件，设置asyncio_mode=auto |
| `backend/tests/test_detectors.py` | 检测器单元测试 |
| `backend/tests/test_api.py` | API集成测试（16个用例）：内存SQLite+dependency_overrides隔离，generate_key()生成测试密钥；基础3个(health/docs/openapi)；检测5个(sensitive_info/all_types/no_sensitive/empty/invalid)；历史8个(空列表/检测后查历史/详情查看验证解密/详情不存在404/删除/删除不存在404/清空验证count/分页) |
| `backend/tests/test_history_service.py` | 历史记录服务单元测试（13个用例）：save基本保存/内容加密验证/结果加密验证、list空列表/分页/排序/不含敏感字段、detail存在记录解密/不存在返回None、delete存在/不存在、clear有记录/空表 |

**前端核心文件**：

| 文件 | 作用 |
|-----|------|
| `frontend/package.json` | Node.js依赖和项目配置（React 18, Vite 5, Tailwind 3等） |
| `frontend/vite.config.ts` | Vite构建配置，配置React插件、代理等 |
| `frontend/tsconfig.json` | TypeScript根配置 |
| `frontend/tsconfig.app.json` | 应用代码TypeScript配置 |
| `frontend/tailwind.config.js` | Tailwind CSS配置，定义扫描路径 |
| `frontend/postcss.config.js` | PostCSS配置，处理Tailwind和 Autoprefixer |
| `frontend/eslint.config.js` | ESLint代码规范配置 |
| `frontend/index.html` | HTML入口文件，root挂载点 |
| `frontend/public/` | 静态资源目录（favicon等） |
| `frontend/src/main.tsx` | React应用入口，createRoot渲染 |
| `frontend/src/App.tsx` | 根组件，配置路由和布局 |
| `frontend/src/index.css` | 全局样式，Tailwind指令 |
| `frontend/src/api/client.ts` | Axios实例，配置baseURL为后端8000端口 |
| `frontend/src/api/detection.ts` | 检测相关API调用（detectText） |
| `frontend/src/api/history.ts` | 历史记录相关API调用（getHistory, deleteHistory, clearHistory） |
| `frontend/src/store/useStore.ts` | Zustand全局状态管理 |
| `frontend/src/pages/DetectPage.tsx` | 检测页面：输入、选择类型、展示结果 |
| `frontend/src/pages/HistoryPage.tsx` | 历史记录页面：列表、删除、分页 |
| `frontend/src/components/` | 可复用的UI组件 |

**数据和配置**：

| 文件 | 作用 |
|-----|------|
| `docker-compose.yml` | 多容器编排：api + web服务 |
| `data/detections.db` | SQLite数据库文件（运行时生成） |
| `data/models/phishing_model.joblib` | 训练好的RandomForest模型 |
| `data/models/tfidf_vectorizer.joblib` | 训练好的TF-IDF向量化器 |
| `data/training/phishing_emails.csv` | 钓鱼邮件训练样本 |
| `data/training/normal_emails.csv` | 正常邮件训练样本 |
| `data/training/phishing_keywords.json` | 中文钓鱼关键词分类词典 |
| `backend/scripts/train_phishing_model.py` | 模型训练脚本 |

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

