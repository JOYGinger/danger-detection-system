# 项目进度追踪

## 当前状态
项目处于 **阶段三步骤 3.2 完成**，弱密码检测器已实现并注册，下一步钓鱼邮件检测（3.3–3.5）或集成测试。

---

## 里程碑

| 里程碑 | 状态 | 开始时间 | 完成时间 |
|-------|------|---------|---------|
| 需求分析 | ✅ 已完成 | - | - |
| 技术选型 | ✅ 已完成 | - | 2026-05-28 |
| 设计文档 | ✅ 已完成 | - | 2026-05-28 |
| 实施计划 | ✅ 已完成 | - | 2026-05-28 |
| 研究资料 | ✅ 已完成 | - | 2026-05-28 |
| 后端开发 | ✅ 已完成 | 2026-05-29 | 2026-05-31 |
| 前端开发 | ✅ 已完成 | 2026-05-31 | 2026-05-31 |
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
- [x] 步骤 2.2：创建FastAPI应用入口
- [x] 步骤 2.3：配置数据库连接
- [x] 步骤 2.4：定义数据库模型
- [x] 步骤 2.5：定义Pydantic模型

### 阶段三：检测器实现
- [x] 步骤 3.1：实现敏感信息检测器（正则+规则引擎）
- [x] 步骤 3.2：实现弱密码检测器（zxcvbn-python）
- [ ] 步骤 3.3：准备钓鱼邮件训练数据（CSV格式）
- [ ] 步骤 3.4：训练钓鱼邮件检测模型
- [ ] 步骤 3.5：实现钓鱼邮件检测器（TF-IDF + RF）
- [ ] 步骤 3.6：创建检测器工厂

### 阶段四：API路由实现
- [x] 步骤 4.1：实现检测API
- [x] 步骤 4.2：实现历史记录服务
- [x] 步骤 4.3：实现历史记录API

### 阶段五：前端实现
- [x] 步骤 5.1：创建API客户端
- [x] 步骤 5.2：创建全局状态管理
- [x] 步骤 5.3：实现检测页面
- [x] 步骤 5.4：实现结果展示组件
- [x] 步骤 5.5：实现历史记录页面
- [x] 步骤 5.6：配置路由和导航

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
| MVP先实现敏感信息检测 | 先打通一个完整链路验证系统可行性，跳过弱密码和钓鱼邮件 | 2026-05-31 |

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

### 2026-06-01
- **步骤 3.2 完成**：实现弱密码检测器
  - 创建 `backend/app/detectors/weak_password.py`：WeakPasswordDetector
    - zxcvbn-python 评估 score 0-4，映射 risk_level（high/high/medium/low/low）
    - details：score/score_max/entropy_bits/guesses/crack_time/feedback/patterns
    - 弱模式中文标签：字典攻击、键盘连续、重复字符、连续序列、日期模式
    - suggestions：zxcvbn 反馈中文化 + NIST 长度建议 + 密码学解读（熵、攻击类型）
    - 全部检测启发式：多行或长度不在 4–128 时跳过，返回 safe + 提示
  - 更新 `backend/app/detectors/__init__.py`：注册 weak_password
  - 更新 `backend/tests/test_detectors.py`：新增 7 个弱密码测试 + 工厂测试
  - 更新 `backend/tests/test_api.py`：新增 weak_password API 测试 2 个
  - 更新 `frontend/src/pages/DetectPage.tsx`：ResultCard 弱密码专用展示；弱密码 placeholder

### 2026-05-31
- **步骤 5.1 完成**：创建API客户端
  - 创建 `frontend/src/api/client.ts`：axios实例，baseURL为空字符串（使用Vite代理转发避免CORS），超时10秒
  - 创建 `frontend/src/api/detection.ts`：检测API
    - `detectText(DetectRequest)` → `DetectResponse`
    - TypeScript接口：DetectRequest、DetectionResult、DetectResponse
  - 创建 `frontend/src/api/history.ts`：历史记录API
    - `getHistory(page, pageSize)` → HistoryList
    - `getHistoryDetail(id)` → HistoryDetail
    - `deleteHistoryItem(id)`、`clearHistory()` → deleted_count
    - TypeScript接口：HistoryItem、HistoryList、HistoryDetail
  - 更新 `frontend/vite.config.ts`：添加代理配置，`/api`和`/health`请求转发到`http://localhost:8000`
  - **CORS解决方案**：使用Vite代理而非修改后端CORS配置，开发环境更安全；生产环境由nginx处理
  - TypeScript编译无错误，浏览器控制台验证API调用成功
- **步骤 5.2 完成**：创建全局状态管理
  - 创建 `frontend/src/store/useStore.ts`：两个Zustand store
    - `useDetectionStore`：currentResult/loading/error状态，detectText()调用API执行检测，clearResult()清空
    - `useHistoryStore`：historyList/historyDetail/historyTotal/historyPage/historyPageSize/loading/error状态，fetchHistory()分页获取、fetchHistoryDetail()获取详情、deleteHistoryItem()删除后自动刷新列表、clearAllHistory()清空
  - TypeScript编译无错误
- **步骤 5.3-5.6 完成**：实现前端全部页面
  - 创建 `frontend/src/pages/DetectPage.tsx`：检测页面
    - 检测类型下拉框（全部/敏感信息/弱密码/钓鱼邮件）
    - 多行文本输入框、开始检测/清空按钮、loading状态
    - ResultCard结果展示组件：风险等级颜色（红high/橙medium/绿low/蓝safe）、置信度、详细发现项、安全建议
    - 单类型显示单个ResultCard，全类型显示多个
  - 创建 `frontend/src/pages/HistoryPage.tsx`：历史记录页面
    - 记录列表（风险等级标签、检测类型、时间、删除按钮）
    - 分页（上一页/下一页）
    - 清空所有（需二次确认，点击按钮后变为"确认清空？"，失焦取消）
  - 更新 `frontend/src/App.tsx`：路由和导航
    - 顶部导航栏（检测/历史两个tab，NavLink激活态高亮）
    - 路由：`/` → 检测页面，`/history` → 历史页面
    - BrowserRouter包裹，Tailwind样式
  - TypeScript编译无错误，浏览器验证检测和历史功能正常
- **步骤 3.1 完成**：实现敏感信息检测器（MVP路径）
  - 创建 `backend/app/detectors/base.py`：DetectionResult数据类(type/risk_level/confidence/details/suggestions)、BaseDetector抽象基类
  - 创建 `backend/app/detectors/sensitive_info.py`：SensitiveInfoDetector
    - 11条检测规则：OpenAI/AWS/GitHub/Google/Stripe API密钥、JWT Token、密码字段、邮箱、手机号、身份证、私钥
    - 掩码函数：API密钥保留前7后3、邮箱保留首字母+域名、手机号前3后4、身份证前6后4、密码完全隐藏
    - 风险计算：有high级发现→high，有medium→medium，否则low
    - 建议生成：根据检测类型给出针对性安全建议
  - 更新 `backend/app/detectors/__init__.py`：工厂函数get_detector()、detect_all()，当前仅注册sensitive_info
  - 创建 `backend/tests/test_detectors.py`：21个测试（基类、工厂、11种类型检测、掩码、位置、建议）
  - 修正OpenAI API密钥正则：`sk-[a-zA-Z0-9]` → `sk-[a-zA-Z0-9_-]`，支持 `sk-proj-` 等含连字符的密钥
  - 全部56个测试通过
- **步骤 4.1 完成**：实现检测API
  - 创建 `backend/app/routers/detection.py`：`POST /api/detect/text`端点
    - 当`detection_type`有值时，调用对应检测器，返回`result`（单类型）
    - 当`detection_type`为空时，调用`detect_all()`，返回`results`（全部类型）
    - 注入`db: Session`依赖（为后续保存历史记录预留）
  - 更新 `backend/app/main.py`：注册detection路由 `app.include_router(detection.router)`
  - 更新 `backend/tests/test_api.py`：新增5个API测试
    - test_detect_sensitive_info：检测敏感信息，验证risk_level=high，count>=2
    - test_detect_all_types：不指定类型，验证results包含sensitive_info
    - test_detect_no_sensitive_info：普通文本，验证risk_level=safe
    - test_detect_empty_content：空内容，验证422
    - test_detect_invalid_type：无效检测类型，验证422
  - 全部61个测试通过
- **步骤 4.2 完成**：实现历史记录服务
  - 创建 `backend/app/services/history.py`：历史记录增删查改服务
    - `save_history(db, content, detection_type, risk_level, result_detail)` - 保存检测记录，input_content和result_detail通过Fernet加密后存储
    - `get_history_list(db, page, page_size)` - 分页获取历史列表（不含敏感字段，按created_at降序）
    - `get_history_detail(db, record_id)` - 获取单条记录详情（解密后返回input_content和result_detail）
    - `delete_history(db, record_id)` - 删除单条记录，不存在返回False
    - `clear_history(db)` - 清空所有记录，返回删除数量
    - DataEncryptor使用延迟初始化（`_get_encryptor()`），避免模块导入时ENCRYPTION_KEY环境变量未设置导致报错
  - 创建 `backend/tests/test_history_service.py`：13个测试
    - TestSaveHistory：基本保存、内容加密验证（密文≠明文）、结果加密验证
    - TestGetHistoryList：空列表、分页（15条分2页）、按created_at降序、不含敏感字段
    - TestGetHistoryDetail：获取存在记录（解密后中文内容正确）、不存在记录返回None
    - TestDeleteHistory：删除存在记录、不存在记录返回False
    - TestClearHistory：清空5条记录返回5、空表返回0
  - 全部74个测试通过
- **步骤 4.3 完成**：实现历史记录API
  - 更新 `backend/app/routers/detection.py`：
    - 检测API接入历史记录保存：单类型检测保存实际detection_type，全类型检测保存detection_type="all"、risk_level取所有结果中最高级别
    - 新增4个历史记录API端点：
      - `GET /api/history` - 分页获取历史列表（page/page_size参数），不含敏感字段（最小化数据暴露原则）
      - `GET /api/history/{record_id}` - 获取单条记录详情（解密后返回input_content和result_detail），不存在返回404
      - `DELETE /api/history/{record_id}` - 删除单条记录，不存在返回404
      - `DELETE /api/history` - 清空所有历史，返回deleted_count
  - 更新 `backend/tests/test_api.py`：
    - 改用内存SQLite数据库 + `dependency_overrides[get_db]`隔离测试数据（每个测试自动建表/清表）
    - 用`generate_key()`生成有效的Fernet测试密钥
    - 新增8个历史记录API测试：空列表、检测后查历史、详情查看（验证解密后input_content正确）、不存在记录404、删除、删除不存在404、清空（验证deleted_count）、分页
  - 全部82个测试通过
  - **验证注意事项**：运行后端需确保`.env`文件存在且`ENCRYPTION_KEY`已填写有效Fernet密钥，否则检测API会500报错
- **步骤 2.5 完成**：定义Pydantic模型
  - 创建 `backend/app/schemas/detection.py`：
    - `DetectionType`枚举：phishing/weak_password/sensitive_info
    - `RiskLevel`枚举：high/medium/low/safe
    - `DetectRequest`：content(min_length=1必填)、detection_type(可选枚举)
    - `DetectResponse`：success(bool)、result(单类型dict)、results(全部类型dict)
    - `HistoryItem`：id/detection_type/risk_level/created_at，不含敏感input_content
    - `HistoryList`：items列表+total/page/page_size分页
    - `HistoryDetail`：含解密后的input_content和result_detail，用于单条记录详情
  - 更新 `backend/app/schemas/__init__.py`：导出所有模型
  - 创建 `backend/tests/test_schemas.py`：13个测试
    - 枚举值验证、空content拒绝、无效detection_type拒绝、单类型/全类型响应、HistoryItem不含敏感字段、分页列表、详情模型
  - 全部35个测试通过
- **步骤 2.4 完成**：定义数据库模型
  - 创建 `backend/app/models/detection.py`：DetectionHistory ORM模型
    - 字段：id(主键自增)、input_content_encrypted(Text非空)、detection_type(String50非空)、risk_level(String20非空)、result_detail_encrypted(Text可空)、created_at(DateTime默认UTC)
    - 索引：idx_created_at、idx_detection_type
    - 使用 `datetime.now(timezone.utc)` 代替已弃用的 `datetime.utcnow()`
  - 更新 `backend/app/models/__init__.py`：导出DetectionHistory
  - 更新 `backend/app/main.py`：添加 `import app.models` 确保init_db()能发现模型建表
  - 创建 `backend/tests/test_models.py`：5个测试（表创建、字段验证、列类型nullable、索引、插入查询）
  - 全部22个测试通过，无警告
  - **PowerShell命令提醒**：Windows PowerShell删除目录用 `Remove-Item -Recurse -Force .venv`，不是CMD的 `rmdir /s /q`
- **步骤 2.3 完成**：配置数据库连接
  - 创建 `backend/app/database.py`：SQLAlchemy引擎、SessionLocal、Base声明基类、init_db()自动建表、get_db()依赖注入
  - init_db()中自动创建data目录（`db_dir.mkdir(parents=True, exist_ok=True)`）
  - 更新 `backend/app/main.py`：使用lifespan上下文管理器，启动时调用init_db()
  - 创建 `backend/tests/test_database.py`：3个测试（init_db建表、get_db会话yield、SessionLocal创建）
  - 全部17个测试通过
  - **环境配置记录**：WSL创建的.venv不能在Windows使用，需先 `rmdir /s /q .venv` 删除，再 `python -m venv .venv` + `pip install -r requirements.txt`
- **步骤 2.2 完成**：创建FastAPI应用入口
  - 创建 `backend/app/main.py`：FastAPI应用实例，配置CORS中间件（仅允许localhost:3000），健康检查端点/health
  - 创建 `backend/app/config.py`：Settings配置类，从环境变量读取ENCRYPTION_KEY、DATABASE_URL、CORS_ORIGINS等
  - 创建 `backend/tests/test_api.py`：3个异步测试全部通过（health_check、openapi_docs、openapi_json）
  - 添加 `python-dotenv==1.0.1` 到 requirements.txt
  - **环境提醒**：WSL创建的.venv不能在Windows使用，需在Windows上重新 `python -m venv .venv` 或 `uv venv` 后再 `pip install -r requirements.txt`
  - **启动命令**：Windows下使用 `python -m uvicorn app.main:app --reload`（直接用uvicorn命令可能不在PATH中）

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

1. **阶段三**：钓鱼邮件检测（3.3–3.5）或 **阶段六** 集成测试

---

## 未来优化

- **敏感信息检测升级为NLP模型**：当前使用正则+规则引擎，无法做语义理解（如"我的密码是admin123"不一定匹配），存在误报可能；后续可升级为DistilBERT等NLP模型，实现语义级别的敏感信息识别，降低误报率、提升对非标准格式的检测能力
