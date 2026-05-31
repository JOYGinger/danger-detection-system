# 项目进度追踪

## 当前状态
项目处于 **规划阶段完成**，已完成全部文档设计和研究资料整理，准备进入开发阶段。

---

## 里程碑

| 里程碑 | 状态 | 开始时间 | 完成时间 |
|-------|------|---------|---------|
| 需求分析 | ✅ 已完成 | - | - |
| 技术选型 | ✅ 已完成 | - | 2026-05-28 |
| 设计文档 | ✅ 已完成 | - | 2026-05-28 |
| 实施计划 | ✅ 已完成 | - | 2026-05-28 |
| 研究资料 | ✅ 已完成 | - | 2026-05-28 |
| 后端开发 | ⏳ 待开始 | - | - |
| 前端开发 | ⏳ 待开始 | - | - |
| 集成测试 | ⏳ 待开始 | - | - |
| Docker部署 | ⏳ 待开始 | - | - |

---

## 详细进度

### 阶段一：项目初始化
- [x] 步骤 1.1：创建项目目录结构
- [x] 步骤 1.2：初始化后端Python环境
- [x] 步骤 1.3：初始化前端项目

### 阶段二：后端基础架构
- [x] 步骤 2.1：创建加密工具模块
- [ ] 步骤 2.2：创建FastAPI应用入口
- [ ] 步骤 2.3：配置数据库连接
- [ ] 步骤 2.4：定义数据库模型
- [ ] 步骤 2.5：定义Pydantic模型

### 阶段三：检测器实现
- [ ] 步骤 3.1：实现敏感信息检测器（正则+规则引擎）
- [ ] 步骤 3.2：实现弱密码检测器（zxcvbn-python）
- [ ] 步骤 3.3：准备钓鱼邮件训练数据（CSV格式）
- [ ] 步骤 3.4：训练钓鱼邮件检测模型
- [ ] 步骤 3.5：实现钓鱼邮件检测器（TF-IDF + RF）
- [ ] 步骤 3.6：创建检测器工厂

### 阶段四：API路由实现
- [ ] 步骤 4.1：实现检测API
- [ ] 步骤 4.2：实现历史记录服务
- [ ] 步骤 4.3：实现历史记录API

### 阶段五：前端实现
- [ ] 步骤 5.1：创建API客户端
- [ ] 步骤 5.2：创建全局状态管理
- [ ] 步骤 5.3：实现检测页面
- [ ] 步骤 5.4：实现结果展示组件
- [ ] 步骤 5.5：实现历史记录页面
- [ ] 步骤 5.6：配置路由和导航

### 阶段六：集成测试
- [ ] 步骤 6.1：后端集成测试
- [ ] 步骤 6.2：前端集成测试
- [ ] 步骤 6.3：端到端测试
- [ ] 步骤 6.4：边界情况测试

### 阶段七：Docker部署
- [ ] 步骤 7.1：创建后端Dockerfile
- [ ] 步骤 7.2：创建前端Dockerfile
- [ ] 步骤 7.3：创建docker-compose配置

### 阶段八：最终验收
- [ ] 步骤 8.1：功能验收测试
- [ ] 步骤 8.2：性能测试
- [ ] 步骤 8.3：更新项目文档

---

## 用户确认的设计决策

| 决策项 | 用户选择 | 确认时间 |
|-------|---------|---------|
| 弱密码检测输入内容保存 | 加密后保存 | 2026-05-28 |
| 钓鱼邮件训练数据 | 由用户提供 | 2026-05-28 |
| 模型文件 | 预先训练 | 2026-05-28 |
| ENCRYPTION_KEY未设置时 | 报错提示用户 | 2026-05-28 |
| 全部检测历史记录 | 一条记录包含三种结果 | 2026-05-28 |
| 钓鱼邮件检测方案 | TF-IDF + RF（MVP），DistilBERT（升级路径） | 2026-05-28 |
| 敏感信息检测方案 | 正则 + 规则引擎 | 2026-05-28 |
| 弱密码检测方案 | 直接使用zxcvbn-python库 | 2026-05-28 |

---

## 技术选型变更记录

| 模块 | 原方案 | 新方案 | 变更理由 | 变更时间 |
|-----|--------|--------|---------|---------|
| 密码强度检测 | 自行实现简化版 | zxcvbn-python | 成熟可靠，社区验证 | 2026-05-28 |
| PII检测 | 纯正则匹配 | 正则+规则引擎 | 参考earlybird设计 | 2026-05-28 |
| 训练数据格式 | 自定义txt | CSV格式 | 便于扩展和处理 | 2026-05-28 |
| 模型保存格式 | 未明确 | joblib | sklearn推荐格式 | 2026-05-28 |

---

## 更新日志

### 2026-05-29
- **步骤 2.1 完成**：创建加密工具模块
  - 创建 `backend/app/utils/crypto.py`：DataEncryptor类（Fernet AES-128-CBC + HMAC-SHA256）
  - 实现 `encrypt()`/`decrypt()` 方法，空字符串直接返回空
  - 实现 `generate_key()` 辅助函数
  - ENCRYPTION_KEY未设置时抛出ValueError
  - 创建 `backend/tests/test_crypto.py`：11个单元测试全部通过
  - 测试覆盖：加解密往返、空字符串、中文、长文本、特殊字符、不同加密产生不同密文、密钥缺失、无效密文、密钥生成
  - 创建 `backend/pyproject.toml`：pytest配置（asyncio_mode=auto）
  - 升级pytest-asyncio修复Python 3.12兼容问题
  - **依赖版本升级**（适配Python 3.13）：
    - scikit-learn: 1.4.0 → 1.5.2
    - numpy: 1.26.3 → 2.1.0
    - cryptography: 42.0.0 → 43.0.0
    - regex: 2023.12.25 → 2024.9.11
    - fastapi: 0.109.0 → 0.115.0
    - uvicorn: 0.27.0 → 0.32.0
    - pydantic: 2.5.3 → 2.10.0
    - pydantic-settings: 2.1.0 → 2.6.0
    - sqlalchemy: 2.0.25 → 2.0.36
    - joblib: 1.3.2 → 1.4.2
    - pytest: 8.0.0 → 8.3.0
    - pytest-asyncio: 0.23.0 → 0.24.0
    - httpx: 0.26.0 → 0.27.0
    - python-multipart: 0.0.6 → 0.0.12
  - **重要提醒**：WSL和Windows环境需分别运行 `pip install -r requirements.txt`

### 2026-05-28
- **步骤 1.3 完成**：初始化前端项目（Vite + React + TypeScript）
  - 使用 `npm create vite` 创建 React+TypeScript 项目
  - 更新 `package.json`，添加依赖：react-router-dom, zustand, axios, clsx, tailwind-merge
  - 安装所有依赖（npm install）
  - 配置 Tailwind CSS：tailwind.config.js, postcss.config.js
  - 创建基础文件：main.tsx, App.tsx, index.css（带Tailwind指令）
  - 创建子目录：src/api/, src/components/, src/pages/, src/store/
- **步骤 1.2 完成**：初始化后端Python环境
  - 创建 `backend/requirements.txt`，包含所有依赖及锁定版本
  - 创建 `backend/.env.example`，包含 `ENCRYPTION_KEY` 和 `DATABASE_URL` 变量模板
  - 依赖：fastapi, uvicorn, sqlalchemy, scikit-learn, jieba, zxcvbn-python, cryptography, pytest等
- **步骤 1.1 完成**：创建项目目录结构
  - 创建 backend/app/ 及其子目录（utils, models, schemas, routers, services, detectors）
  - 创建 backend/tests/
  - 创建 frontend/src/ 及其子目录（api, components, pages, store）
  - 创建 data/models/ 和 data/training/
  - 创建所有 `__init__.py` 文件
- 更新技术选型文档（tech-stack.md）
  - 密码强度检测改用zxcvbn-python
  - 敏感信息检测采用正则+规则引擎方案
  - 明确加密方案为Fernet
- 更新架构文档（architecture.md）
  - 添加信息安全知识点说明
  - 更新目录结构（添加utils/、data/models/等）
  - 添加加密存储设计
- 更新实施计划（implementation-plan.md）
  - 更新检测器实现方案
  - 添加训练数据格式说明（CSV）
  - 添加信息安全知识点索引
- 更新设计文档（design-document.md）
  - 添加信息安全课程内容体现章节
  - 添加安全设计章节
  - 添加学习路径说明
- 通过GitHub API和arXiv API检索学术资源：
  - 钓鱼邮件检测：5篇arXiv论文 + 10个GitHub项目
  - PII检测：3篇arXiv论文 + 7个GitHub项目
  - 密码强度：6篇arXiv论文 + 7个zxcvbn实现
  - 数据库加密：SQLCipher等开源方案

### 2026-05-21
- 完成设计文档编写
- 完成技术栈选型
- 完成实施计划编写
- 创建 memory-bank 目录结构
- 创建 research 目录
- 完成4份研究资料整理：
  - `/research/phishing-detection-nlp.md` - 钓鱼邮件NLP检测研究
  - `/research/sensitive-data-masking.md` - 敏感信息掩码技术
  - `/research/database-security-storage.md` - 数据库安全存储技术
  - `/research/password-strength-detection.md` - 密码强度检测技术

---

## 下一步计划

1. **开始阶段一：项目初始化**
   - 创建项目目录结构
   - 初始化后端Python环境（requirements.txt, .env.example）
   - 初始化前端项目（Vite + React + TypeScript）

2. **准备工作**
   - 用户提供钓鱼邮件训练数据
   - 生成ENCRYPTION_KEY并配置环境变量
