# 危险检测集成系统 - 实施计划

本文档包含一系列给AI开发者的分步指令，每一步都小而具体，并包含验证正确性的测试方法。

**重要**：执行任何代码编写前，请先阅读 `/research` 目录下的相关研究文档。

---

## 阶段一：项目初始化

### 步骤 1.1：创建项目目录结构
**指令**：按照 `memory-bank/architecture.md` 中定义的目录结构，创建 backend 和 frontend 两个主目录，以及所有必要的子目录和空白的 `__init__.py` 文件。

**验证**：
- 运行 `find . -type d` 检查目录结构是否完整
- 确认所有 `__init__.py` 文件已创建

---

### 步骤 1.2：初始化后端Python环境
**指令**：在 backend 目录下创建 requirements.txt 文件，内容严格按照 `memory-bank/tech-stack.md` 中定义的依赖版本。创建 `.env.example` 文件作为环境变量模板，包含 `ENCRYPTION_KEY` 和 `DATABASE_URL` 变量。

**验证**：
- 运行 `pip install -r backend/requirements.txt` 确认所有依赖可正常安装
- 检查无版本冲突警告

---

### 步骤 1.3：初始化前端项目
**指令**：在 frontend 目录下使用 Vite 创建 React+TypeScript 项目，安装 `memory-bank/tech-stack.md` 中列出的所有依赖。配置 Tailwind CSS、ESLint 和 Prettier。

**验证**：
- 运行 `npm run dev` 确认开发服务器可正常启动
- 访问默认页面确认 React 应用正常运行
- 运行 `npm run lint` 确认 ESLint 配置正确

---

## 阶段二：后端基础架构

### 步骤 2.1：创建加密工具模块
**指令**：在 `backend/app/utils/crypto.py` 中创建数据加密工具类 `DataEncryptor`，使用 Fernet（AES-128-CBC + HMAC）实现加密和解密功能。参考 `/research/database-security-storage.md` 中的实现方案。

**信息安全知识点**：
- 对称加密原理
- 加密与认证（Authenticated Encryption）
- 密钥管理最佳实践

**实现要点**：
```python
class DataEncryptor:
    def __init__(self):
        # 从环境变量读取密钥，未设置则报错退出
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY环境变量未设置")
        self.cipher = Fernet(key.encode())
    
    def encrypt(self, plaintext: str) -> str: ...
    def decrypt(self, ciphertext: str) -> str: ...
```

**验证**：
- 编写单元测试，验证加密后的密文可正确解密还原
- 测试空字符串处理
- 测试中文内容加密解密
- 测试未设置密钥时抛出正确异常

---

### 步骤 2.2：创建FastAPI应用入口
**指令**：在 `backend/app/main.py` 中创建 FastAPI 应用实例，配置 CORS 中间件允许前端访问（允许 `localhost:3000`），添加基本的健康检查端点 `/health`。从环境变量读取配置。

**信息安全知识点**：
- CORS（跨域资源共享）安全配置
- 最小权限原则（仅允许可信源）

**验证**：
- 运行 `uvicorn app.main:app --reload` 启动服务
- 访问 `/health` 端点确认返回 `{"status": "ok"}`
- 访问 `/docs` 确认 Swagger 文档自动生成

---

### 步骤 2.3：配置数据库连接
**指令**：在 `backend/app/database.py` 中配置 SQLite 数据库连接，使用 SQLAlchemy 创建引擎。数据库文件路径为 `./data/detections.db`。在应用启动时自动创建表结构。

**验证**：
- 启动应用后检查 data 目录下是否自动创建 detections.db 文件
- 使用 SQLite Browser 打开数据库文件确认文件有效

---

### 步骤 2.4：定义数据库模型
**指令**：在 `backend/app/models/detection.py` 中定义 DetectionHistory 模型，字段包括：
- `id`（主键）
- `input_content_encrypted`（加密后的输入内容）
- `detection_type`（字符串：phishing/weak_password/sensitive_info/all）
- `risk_level`（字符串：high/medium/low/safe）
- `result_detail_encrypted`（加密后的检测结果JSON）
- `created_at`（时间戳）

**信息安全知识点**：
- 数据分类与分级
- 敏感字段识别与保护

**验证**：
- 启动应用后使用 SQLite Browser 检查表结构是否正确创建
- 确认敏感字段命名包含 `_encrypted` 后缀

---

### 步骤 2.5：定义Pydantic模型
**指令**：在 `backend/app/schemas/detection.py` 中定义请求和响应模型：
- `DetectRequest`：content（字符串）、detection_type（可选枚举：phishing/weak_password/sensitive_info）
- `DetectResponse`：success（布尔）、result（字典）
- `HistoryItem`：id、detection_type、risk_level、created_at（不返回敏感的input_content）
- `HistoryList`：HistoryItem 列表，包含分页信息

**信息安全知识点**：
- 输入验证（Input Validation）
- 最小化数据暴露原则

**验证**：
- 编写 pytest 测试，导入模型创建实例确认字段验证正常
- 测试无效输入时抛出验证错误
- 测试枚举值验证

---

## 阶段三：检测器实现

### 步骤 3.1：实现敏感信息检测器
**指令**：在 `backend/app/detectors/sensitive_info.py` 中实现敏感信息检测器，采用"正则+规则引擎"方案。参考 `/research/sensitive-data-masking.md` 和 GitHub项目 earlybird 的设计。

**信息安全知识点**：
- PII（个人身份信息）识别
- DLP（数据泄露防护）基础
- 正则表达式在安全检测中的应用

**检测类型**：

| 优先级 | 类型 | 正则模式示例 |
|-------|------|-------------|
| P0 | OpenAI API密钥 | `sk-[a-zA-Z0-9]{20,}` |
| P0 | AWS密钥 | `AKIA[0-9A-Z]{16}` |
| P0 | GitHub Token | `ghp_[a-zA-Z0-9]{36}` |
| P0 | JWT Token | `eyJ[a-zA-Z0-9-_]+\.` |
| P0 | 密码字段 | `password\s*[=:]\s*\S+` |
| P1 | 邮箱地址 | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` |
| P1 | 手机号(中国) | `1[3-9]\d{9}` |
| P2 | 身份证号 | `\d{17}[\dXx]` |

**返回内容**：
- 检测到的敏感信息类型
- 掩码后的值（如 `sk-proj-****xyz`）
- 位置信息（start, end）
- 风险等级
- 掩码建议

**验证**：
- 编写 pytest 单元测试，输入包含 API 密钥的文本，确认能正确识别
- 输入包含多种敏感信息的文本，确认返回所有检测结果
- 输入普通文本，确认返回空结果
- 测试掩码函数输出格式正确

---

### 步骤 3.2：实现弱密码检测器
**指令**：在 `backend/app/detectors/weak_password.py` 中实现弱密码检测器，直接调用 zxcvbn-python 库。参考 `/research/password-strength-detection.md`。

**信息安全知识点**：
- 密码学基础：熵值（Entropy）
- 密码攻击方式：暴力破解、字典攻击、模式匹配
- 密码强度评估原理

**实现要点**：
```python
from zxcvbn import zxcvbn

def detect(password: str) -> DetectionResult:
    result = zxcvbn(password)
    score = result['score']  # 0-4
    # 转换为风险等级
    risk_level = ['high', 'high', 'medium', 'low', 'low'][score]
    ...
```

**返回内容**：
- 强度评分（0-4）
- 风险等级
- 熵值估算
- 破解时间
- 具体反馈列表
- 改进建议列表

**验证**：
- 编写 pytest 测试
- 输入 "password123"，确认返回高风险评分
- 输入 "Tr0ub4dor&3App!"，确认返回低风险评分
- 输入空字符串，确认正确处理边界情况

---

### 步骤 3.3：准备钓鱼邮件训练数据
**指令**：创建 `backend/data/training/` 目录，准备钓鱼邮件检测的训练数据，使用CSV格式（便于扩展）：

1. 创建 `phishing_emails.csv`，包含钓鱼邮件样本
   - 列：id, text, label(=1)
2. 创建 `normal_emails.csv`，包含正常邮件样本
   - 列：id, text, label(=0)
3. 创建 `phishing_keywords.json`，整理中文钓鱼词汇分类

参考 `/research/phishing-detection-nlp.md` 中的词汇分类。

**信息安全知识点**：
- 社会工程学（Social Engineering）
- 钓鱼攻击心理学原理
- 中文钓鱼邮件特征分析

**验证**：
- 检查CSV文件格式正确
- 确认词汇列表包含必要的分类（紧迫性、威胁性、诱导性、伪装性）

---

### 步骤 3.4：训练钓鱼邮件检测模型
**指令**：创建 `backend/scripts/train_phishing_model.py`，使用 scikit-learn 训练模型：

**信息安全知识点**：
- 机器学习在安全领域的应用
- TF-IDF文本特征提取
- 分类模型评估指标

**实现流程**：
1. 读取训练数据（CSV格式）
2. 使用 jieba 进行中文分词
3. 使用 TfidfVectorizer 提取文本特征
4. 训练 RandomForest 分类器
5. 保存模型和向量化器到 `data/models/` 目录（joblib格式）

**验证**：
- 运行训练脚本，确认生成模型文件
- 模型文件路径：`data/models/phishing_model.joblib`
- 向量化器路径：`data/models/tfidf_vectorizer.joblib`

---

### 步骤 3.5：实现钓鱼邮件检测器
**指令**：在 `backend/app/detectors/phishing.py` 中实现钓鱼邮件检测器，加载预训练模型进行检测。参考 `/research/phishing-detection-nlp.md`。

**信息安全知识点**：
- NLP在钓鱼检测中的应用
- 模型推理流程
- 置信度与阈值设置

**实现要点**：
```python
class PhishingDetector(BaseDetector):
    def __init__(self):
        self.model = joblib.load('data/models/phishing_model.joblib')
        self.vectorizer = joblib.load('data/models/tfidf_vectorizer.joblib')
    
    def detect(self, content: str) -> DetectionResult:
        words = jieba.cut(content)
        text = ' '.join(words)
        features = self.vectorizer.transform([text])
        prediction = self.model.predict(features)[0]
        proba = self.model.predict_proba(features)[0]
        ...
```

**返回内容**：
- 风险等级（高/中/低）
- 置信度（0-1）
- 判定依据列表
- 安全建议

**验证**：
- 编写 pytest 测试
- 输入包含 "立即点击链接验证账户" 的文本，确认返回高风险
- 输入正常商务邮件文本，确认返回低风险
- 测试模型文件不存在时的错误处理

---

### 步骤 3.6：创建检测器工厂
**指令**：在 `backend/app/detectors/__init__.py` 中创建检测器工厂函数和统一的检测器接口。

**接口定义**：
```python
class DetectionResult:
    type: str           # 检测类型
    risk_level: str     # 风险等级: high/medium/low/safe
    confidence: float   # 置信度
    details: dict       # 详细结果
    suggestions: list   # 安全建议

class BaseDetector:
    def detect(self, content: str) -> DetectionResult
```

**工厂函数**：
- `get_detector(detection_type: str) -> BaseDetector`
- `detect_all(content: str) -> Dict[str, DetectionResult]` 运行所有检测器

**验证**：
- 编写 pytest 测试
- 调用工厂函数传入 "phishing"，确认返回钓鱼邮件检测器
- 调用工厂函数传入 "weak_password"，确认返回弱密码检测器
- 调用工厂函数传入 "sensitive_info"，确认返回敏感信息检测器
- 调用 detect_all 确认返回三个检测结果

---

## 阶段四：API路由实现

### 步骤 4.1：实现检测API
**指令**：在 `backend/app/routers/detection.py` 中实现 `POST /api/detect/text` 接口。

**功能**：
- 接收文本内容和检测类型
- 如果指定类型，调用对应检测器
- 如果未指定类型，调用 `detect_all` 运行所有检测器
- 返回检测结果
- 调用历史记录服务保存记录（加密存储）

**验证**：
- 使用 pytest 或 curl 发送 POST 请求
- 指定 phishing 类型，确认返回正确格式
- 不指定类型，确认返回所有检测结果
- 发送空内容，确认返回 400 错误

---

### 步骤 4.2：实现历史记录服务
**指令**：在 `backend/app/services/history.py` 中实现历史记录的增删改查功能。

**信息安全知识点**：
- 数据生命周期管理
- 加密存储实现

**功能**：
- `save_history(content, detection_type, result)` - 保存检测记录（敏感字段加密）
- `get_history(page, page_size)` - 分页获取历史列表
- `get_history_by_id(id)` - 获取单条记录详情（解密后返回）
- `delete_history(id)` - 删除单条记录
- `clear_history()` - 清空所有记录

**验证**：
- 编写 pytest 测试
- 执行保存后从数据库验证数据已加密存储
- 测试读取时正确解密
- 测试分页功能
- 测试删除功能

---

### 步骤 4.3：实现历史记录API
**指令**：在 `backend/app/routers/detection.py` 中添加以下接口：
- `GET /api/history` - 获取历史列表（支持 page 和 page_size 参数）
- `GET /api/history/{id}` - 获取单条记录详情
- `DELETE /api/history/{id}` - 删除单条记录
- `DELETE /api/history` - 清空所有历史

**验证**：
- 编写 pytest 测试每个接口
- 测试返回格式符合设计
- 测试删除不存在的记录，确认返回 404
- 测试分页参数正常工作

---

## 阶段五：前端实现

### 步骤 5.1：创建API客户端
**指令**：在 `frontend/src/api/` 目录下创建 HTTP 客户端，使用 axios 封装所有后端 API 调用。

**文件结构**：
- `client.ts` - axios 实例配置，baseURL 为 `http://localhost:8000`
- `detection.ts` - 检测相关 API（detectText）
- `history.ts` - 历史记录相关 API（getHistory, deleteHistory, clearHistory）

**验证**：
- 在浏览器控制台测试 API 调用函数
- 确认网络请求正确发送到后端
- 确认错误响应被正确捕获

---

### 步骤 5.2：创建全局状态管理
**指令**：使用 Zustand 创建全局 store，管理以下状态：

**状态**：
- `currentResult` - 当前检测结果（单类型或所有类型）
- `historyList` - 历史记录列表
- `loading` - 加载状态
- `error` - 错误信息

**Actions**：
- `detectText` - 执行检测
- `fetchHistory` - 获取历史
- `deleteHistoryItem` - 删除历史项
- `clearAllHistory` - 清空历史

**验证**：
- 使用 Jest 和 React Testing Library 测试
- 在组件中调用 store 的 action，确认状态更新

---

### 步骤 5.3：实现检测页面
**指令**：创建首页组件，包含以下元素：

**UI组件**：
- 多行文本输入框（支持大量文本）
- 检测类型下拉框（全部/钓鱼邮件/弱密码/敏感信息）
- 检测按钮
- 加载状态指示器

**使用 Tailwind CSS 进行样式设计**。

**验证**：
- 使用 Jest 和 React Testing Library 测试组件渲染
- 在浏览器中检查页面布局正确
- 测试输入框输入大量文本时的表现
- 检查响应式布局

---

### 步骤 5.4：实现结果展示组件
**指令**：创建结果展示组件，根据检测类型显示不同格式。

**显示逻辑**：
- 单类型检测：显示单一结果区域
- 全部检测：分三栏展示三种检测结果

**样式要求**：
- 风险等级颜色：红色(高)、橙色(中)、绿色(低)、蓝色(安全)
- 清晰展示判定依据和建议列表

**验证**：
- 测试三种检测类型的展示格式
- 检查风险等级颜色正确
- 测试分栏布局

---

### 步骤 5.5：实现历史记录页面
**指令**：创建历史记录页面组件，以列表形式展示历史检测记录。

**显示内容**：
- 检测类型（带图标或颜色区分）
- 风险等级
- 检测时间
- 操作按钮（查看详情、删除）

**功能**：
- 分页加载（每页10条）
- 清空所有按钮（需确认）

**验证**：
- 执行多次检测后访问历史页面，确认记录正确显示
- 测试删除功能
- 测试分页功能

---

### 步骤 5.6：配置路由和导航
**指令**：使用 react-router-dom 配置应用路由。

**路由配置**：
- `/` - 检测页面
- `/history` - 历史记录页面

**导航组件**：
- 页面顶部导航栏
- 包含"检测"和"历史记录"两个链接

**验证**：
- 使用 Jest 测试路由跳转
- 访问 `/` 确认显示检测页面
- 访问 `/history` 确认显示历史页面

---

## 阶段六：集成测试

### 步骤 6.1：后端集成测试
**指令**：编写 pytest 集成测试，覆盖完整的 API 调用流程。

**测试用例**：
- 完整的检测流程（请求 → 处理 → 存储 → 响应）
- 历史记录 CRUD 操作
- 数据加密存储验证
- 并发请求处理

**验证**：
- 运行 `pytest backend/tests/ -v` 确认所有测试通过
- 检查测试覆盖率

---

### 步骤 6.2：前端集成测试
**指令**：使用 Jest 和 React Testing Library 编写前端集成测试。

**测试用例**：
- 检测页面交互流程
- API 调用 mock 测试
- 路由导航测试
- 错误状态处理

**验证**：
- 运行 `npm test` 确认所有测试通过

---

### 步骤 6.3：端到端测试
**指令**：启动前后端服务，在浏览器中执行完整的检测流程。

**测试流程**：
1. 输入钓鱼邮件文本，选择"钓鱼邮件"类型，点击检测
2. 查看结果展示
3. 访问历史记录页面，确认记录已保存
4. 测试弱密码检测
5. 测试敏感信息检测
6. 测试"全部检测"模式

**验证**：
- 确认三种类型检测都能正常工作
- 确认响应时间在 5 秒以内
- 确认历史记录正确保存

---

### 步骤 6.4：边界情况测试
**指令**：测试以下边界情况：
- 空输入
- 超长文本（10000字符）
- 特殊字符输入
- 网络断开时的错误处理
- 并发多个检测请求

**验证**：
- 确认空输入返回明确的错误提示
- 确认超长文本不会导致服务崩溃
- 确认网络错误有友好的提示信息

---

## 阶段七：Docker部署

### 步骤 7.1：创建后端Dockerfile
**指令**：在 backend 目录下创建 Dockerfile。

**配置要求**：
- 基础镜像：`python:3.11-slim`
- 安装依赖
- 预下载jieba词典
- 配置启动命令
- 设置环境变量

**验证**：
- 运行 `docker build -t security-backend ./backend` 构建镜像
- 运行 `docker run -p 8000:8000 -e ENCRYPTION_KEY=test_key security-backend` 启动容器
- 访问 `/health` 确认服务正常

---

### 步骤 7.2：创建前端Dockerfile
**指令**：在 frontend 目录下创建 Dockerfile，使用多阶段构建。

**配置要求**：
- 第一阶段：使用 `node:20-alpine` 构建 React 应用
- 第二阶段：使用 `nginx:alpine` 提供静态文件服务
- 创建 `nginx.conf` 处理 SPA 路由

**验证**：
- 运行 `docker build -t security-frontend ./frontend` 构建镜像
- 运行 `docker run -p 3000:80 security-frontend` 启动容器
- 访问页面确认应用正常加载

---

### 步骤 7.3：创建docker-compose配置
**指令**：在项目根目录创建 `docker-compose.yml`。

**服务配置**：
- api 服务：端口 8000，挂载数据卷，健康检查
- web 服务：端口 3000，依赖 api
- 配置网络
- 设置环境变量

**验证**：
- 运行 `docker-compose up -d` 启动所有服务
- 访问前端页面，执行检测功能确认前后端通信正常
- 运行 `docker-compose down` 确认正常停止

---

## 阶段八：最终验收

### 步骤 8.1：功能验收测试
**指令**：按照 `memory-bank/design-document.md` 中的验收标准逐项测试。

**验收清单**：
1. 用户输入文本内容后，5秒内返回检测结果
2. 检测结果包含风险等级和判定依据
3. 历史记录正确保存和展示
4. Docker部署后可直接访问Web界面
5. 所有界面文字为简体中文

**验证**：
- 逐项检查并记录结果

---

### 步骤 8.2：性能测试
**指令**：测试系统在多次检测下的性能表现。

**测试内容**：
- 连续执行10次检测，记录响应时间
- 检查内存使用是否正常
- 检查数据库文件大小

**验证**：
- 确认响应时间稳定在5秒以内
- 确认无内存泄漏
- 确认数据库文件大小合理

---

### 步骤 8.3：更新项目文档
**指令**：完成所有功能后，更新以下文档：
- `memory-bank/progress.md` - 标记所有步骤为已完成
- `memory-bank/architecture.md` - 更新架构说明（如有变化）

---

## 附录：测试用例参考

### 钓鱼邮件检测测试用例
| 输入 | 预期风险等级 |
|------|-------------|
| "您的账户存在异常，请立即点击 http://xxx.com 验证身份，否则将被冻结" | 高 |
| "您好，关于上次商务合作的方案已发送附件，请查收" | 低 |
| "紧急通知！系统检测到您的账户存在安全风险，请立即修改密码" | 中 |

### 弱密码检测测试用例
| 输入 | 预期评分 | 风险等级 |
|------|---------|---------|
| "password" | 0 | 高 |
| "Password1" | 2 | 中 |
| "Tr0ub4dor&3App!" | 4 | 低 |

### 敏感信息检测测试用例
| 输入 | 预期检测类型 |
|------|-------------|
| "API密钥：sk-1234567890abcdef" | API密钥(OpenAI) |
| "联系邮箱：test@example.com" | 邮箱地址 |
| "password=admin123" | 密码字段 |
| "AWS Key: AKIAIOSFODNN7EXAMPLE" | API密钥(AWS) |

---

## 附录：中文钓鱼词汇列表

### 紧迫性词汇
立即、紧急、马上、尽快、限时、最后机会、今日截止、即将过期

### 威胁性词汇
冻结、封禁、异常、风险、安全、验证、锁定、暂停、停止服务

### 诱导性词汇
点击、链接、验证身份、确认信息、领取奖励、免费、优惠、中奖

### 伪装性词汇
官方、客服、银行、支付宝、微信支付、淘宝、京东、税务局、公安局

---

## 附录：信息安全知识点索引

| 阶段 | 步骤 | 知识点 |
|-----|------|--------|
| 二 | 2.1 | 对称加密、密钥管理 |
| 二 | 2.2 | CORS安全配置 |
| 二 | 2.4 | 数据分类与分级 |
| 二 | 2.5 | 输入验证 |
| 三 | 3.1 | PII识别、DLP、正则表达式 |
| 三 | 3.2 | 密码学熵值、密码攻击方式 |
| 三 | 3.3 | 社会工程学、钓鱼心理学 |
| 三 | 3.4 | ML在安全领域应用 |
| 三 | 3.5 | NLP安全应用、置信度 |
| 四 | 4.2 | 数据生命周期管理、加密存储 |
