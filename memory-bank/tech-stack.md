# 技术栈推荐

## 1. 技术选型总览

| 层级 | 技术选型 | 版本 | 推荐理由 |
|-----|---------|------|---------|
| 前端框架 | React | 18.x | 生态成熟，组件化开发效率高 |
| 语言 | TypeScript | 5.x | 类型安全，减少运行时错误 |
| UI框架 | Tailwind CSS | 3.x | 原子化CSS，定制灵活 |
| 状态管理 | Zustand | 4.x | 轻量级，API简洁 |
| 后端框架 | FastAPI | 0.109.x | 异步高性能，自动生成API文档 |
| 语言 | Python | 3.11 | 丰富的安全检测库支持 |
| 数据库 | SQLite | - | 轻量级，无需额外服务 |
| ORM | SQLAlchemy | 2.x | Python最流行的ORM |
| NLP处理 | scikit-learn | 1.4.x | 文本特征提取与分类 |
| NLP处理 | jieba | 0.42.x | 中文分词 |
| 密码强度 | zxcvbn-python | 4.4.x | 成熟的密码强度评估库 |
| 加密存储 | cryptography | 42.x | Fernet/AES-GCM加密 |
| 部署 | Docker | 24.x | 容器化部署 |
| 容器编排 | Docker Compose | 2.x | 简化多容器管理 |

---

## 2. 前端技术栈

### 2.1 核心依赖

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "zustand": "^4.5.0",
    "axios": "^1.6.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "vite": "^5.1.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.56.0",
    "prettier": "^3.2.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0"
  }
}
```

### 2.2 开发工具

| 工具 | 用途 |
|-----|------|
| Vite | 构建工具，速度快 |
| ESLint | 代码质量检查 |
| Prettier | 代码格式化 |
| Tailwind CSS | 原子化CSS样式 |
| Jest + React Testing Library | 前端测试 |

---

## 3. 后端技术栈

### 3.1 核心依赖

```txt
# Web框架
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6

# 数据库
sqlalchemy==2.0.25

# NLP处理 - 钓鱼邮件检测
scikit-learn==1.4.0
jieba==0.42.1
numpy==1.26.3
joblib==1.3.2

# 密码强度检测 - 使用成熟库
zxcvbn-python==4.4.2

# 数据加密存储
cryptography==42.0.0

# 正则增强
regex==2023.12.25

# 测试
pytest==8.0.0
pytest-asyncio==0.23.0
httpx==0.26.0
```

### 3.2 技术选型变更说明

| 模块 | 原方案 | 新方案 | 变更理由 |
|-----|--------|--------|---------|
| 密码强度检测 | 自行实现简化版 | zxcvbn-python | 成熟可靠，714+ stars，社区验证 |
| PII检测 | 纯正则匹配 | 正则+规则引擎 | 参考earlybird设计，提升准确率 |
| 加密方案 | Fernet | Fernet/AES-GCM | 明确加密模式，符合安全规范 |

### 3.3 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── utils/
│   │   ├── __init__.py
│   │   └── crypto.py        # 加密工具类
│   ├── models/
│   │   ├── __init__.py
│   │   └── detection.py     # SQLAlchemy ORM模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── detection.py     # Pydantic请求/响应模型
│   ├── routers/
│   │   ├── __init__.py
│   │   └── detection.py     # API路由
│   ├── services/
│   │   ├── __init__.py
│   │   ├── detector.py      # 检测服务
│   │   └── history.py       # 历史记录服务
│   └── detectors/
│       ├── __init__.py      # 检测器工厂
│       ├── base.py          # 检测器基类
│       ├── phishing.py      # 钓鱼邮件检测（TF-IDF + RF）
│       ├── weak_password.py # 弱密码检测（zxcvbn）
│       └── sensitive_info.py # 敏感信息检测（正则+规则引擎）
├── data/
│   ├── detections.db        # SQLite数据库
│   ├── models/              # 训练好的模型文件
│   │   └── phishing_model.joblib
│   └── training/            # 训练数据
│       ├── phishing_emails.csv
│       ├── normal_emails.csv
│       └── phishing_keywords.json
├── tests/
│   ├── __init__.py
│   ├── test_detectors.py
│   ├── test_api.py
│   └── test_crypto.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

## 4. 数据库设计

### 4.1 表结构

```sql
-- 检测历史表
CREATE TABLE detection_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_content_encrypted TEXT NOT NULL,  -- AES-256加密后的输入内容
    detection_type TEXT NOT NULL,           -- 'phishing', 'weak_password', 'sensitive_info', 'all'
    risk_level TEXT NOT NULL,               -- 'high', 'medium', 'low', 'safe'
    result_detail_encrypted TEXT,           -- AES-256加密后的检测结果（JSON格式）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_created_at ON detection_history(created_at DESC);
CREATE INDEX idx_detection_type ON detection_history(detection_type);
```

### 4.2 加密存储设计

| 字段 | 存储方式 | 加密算法 | 说明 |
|-----|---------|---------|------|
| input_content_encrypted | 密文 | Fernet (AES-128-CBC + HMAC) | 用户输入内容 |
| result_detail_encrypted | 密文 | Fernet (AES-128-CBC + HMAC) | 检测结果JSON |
| detection_type | 明文 | - | 非敏感元数据 |
| risk_level | 明文 | - | 非敏感结果 |
| created_at | 明文 | - | 时间戳 |

---

## 5. API 设计

### 5.1 接口列表

| 方法 | 路径 | 描述 |
|-----|------|------|
| POST | /api/detect/text | 文本内容检测 |
| GET | /api/history | 获取检测历史（分页） |
| GET | /api/history/{id} | 获取单条记录详情 |
| DELETE | /api/history/{id} | 删除单条历史 |
| DELETE | /api/history | 清空所有历史 |
| GET | /health | 健康检查 |

### 5.2 请求/响应示例

**POST /api/detect/text**

```json
// Request - 单类型检测
{
  "content": "您的账户存在异常，请立即点击链接验证身份...",
  "detection_type": "phishing"
}

// Request - 全部检测
{
  "content": "sk-proj-abc123 password=admin123 您的账户异常请点击链接"
}

// Response - 钓鱼邮件检测
{
  "success": true,
  "result": {
    "type": "phishing",
    "risk_level": "high",
    "confidence": 0.85,
    "reasons": [
      "包含诱导性紧迫语言",
      "存在可疑链接",
      "要求提供敏感信息"
    ],
    "suggestions": [
      "不要点击陌生链接",
      "通过官方渠道验证信息"
    ]
  }
}

// Response - 弱密码检测
{
  "success": true,
  "result": {
    "type": "weak_password",
    "risk_level": "high",
    "score": 1,
    "score_max": 4,
    "entropy": 18.5,
    "crack_time": "少于1分钟",
    "feedback": ["密码太常见", "缺少数字和特殊字符"],
    "suggestions": ["使用至少8位密码", "包含大小写字母、数字和特殊字符"]
  }
}

// Response - 敏感信息检测
{
  "success": true,
  "result": {
    "type": "sensitive_info",
    "risk_level": "high",
    "findings": [
      {
        "type": "api_key_openai",
        "label": "OpenAI API密钥",
        "masked_value": "sk-proj-****789",
        "position": {"start": 0, "end": 20},
        "risk": "high"
      },
      {
        "type": "password_field",
        "label": "密码字段",
        "masked_value": "password=******",
        "position": {"start": 21, "end": 37},
        "risk": "high"
      }
    ],
    "suggestions": [
      "使用环境变量代替硬编码密钥",
      "敏感信息不应提交到版本控制系统"
    ]
  }
}

// Response - 全部检测（detection_type为空时）
{
  "success": true,
  "results": {
    "phishing": { ... },
    "weak_password": { ... },
    "sensitive_info": { ... }
  }
}
```

---

## 6. 检测器技术方案

### 6.1 钓鱼邮件检测器

**当前方案（MVP）：**

| 组件 | 技术 | 说明 |
|-----|------|------|
| 分词 | jieba | 中文分词 |
| 特征提取 | TF-IDF | 文本向量化 |
| 分类器 | RandomForest | 集成学习，可解释性强 |
| 模型存储 | joblib | 序列化模型文件 |

**升级路径（可选）：**

| 升级方案 | 技术 | 预期提升 | 资源需求 |
|---------|------|---------|---------|
| 进阶 | XGBoost | +3-5%准确率 | 低 |
| 高级 | DistilBERT中文 | +8-12%准确率 | 需GPU训练 |

### 6.2 弱密码检测器

**方案：直接使用 zxcvbn-python**

```python
from zxcvbn import zxcvbn

result = zxcvbn("Tr0ub4dor&3")
# 返回: score(0-4), crack_time, feedback等
```

**优势：**
- 完整的模式匹配（字典、键盘、日期、重复等）
- 计算熵值和破解时间
- 提供具体的改进建议
- 社区验证，持续维护

### 6.3 敏感信息检测器

**方案：正则 + 规则引擎（参考earlybird）**

| 检测类型 | 方法 | 规则来源 |
|---------|------|---------|
| API密钥 | 正则匹配 | 已知前缀库 |
| 密码字段 | 正则匹配 | password=, pwd=等模式 |
| JWT Token | 正则匹配 | eyJ开头 |
| 邮箱/手机/身份证 | 正则匹配 | 标准格式 |
| 私钥文件 | 正则匹配 | PEM格式标识 |
| 自定义敏感词 | 规则引擎 | 可配置扩展 |

---

## 7. Docker 配置

### 7.1 Dockerfile (后端)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 下载jieba词典（缓存）
RUN python -c "import jieba; jieba.initialize()"

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data/models /app/data/training

EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 Dockerfile (前端)

```dockerfile
# 构建阶段
FROM node:20-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 7.3 docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - DATABASE_URL=sqlite:///app/data/detections.db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - api
```

---

## 8. 版本锁定建议

所有依赖版本在 `requirements.txt` 和 `package.json` 中锁定具体版本，避免因依赖更新导致兼容性问题。

生产环境使用 `npm ci` 和 `pip install -r requirements.txt` 确保一致性。

---

## 9. 参考资源

### 学术论文
- [Phishsense-1B](https://arxiv.org/abs/2503.10944) - LLM钓鱼检测，97.5%准确率
- [Adversarial ML for Password Strength](https://arxiv.org/abs/2506.00373) - 对抗训练方法
- [PII-Bench](https://arxiv.org/abs/2502.18545) - PII保护评估框架

### 开源项目
- [zxcvbn-python](https://github.com/dwolfhub/zxcvbn-python) - 密码强度检测
- [earlybird](https://github.com/americanexpress/earlybird) - 敏感数据检测
- [Email-Phishing-NLP](https://github.com/mo-messidi/Email-Phishing-Attempts-Detection-using-NLP) - 钓鱼邮件检测

### 标准规范
- NIST SP 800-63B: 数字身份指南
- OWASP Top 10: Web应用安全风险
- PCI DSS: 支付卡行业数据安全标准
