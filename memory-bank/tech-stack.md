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
| 密码分析 | zxcvbn | 4.4.x | 密码强度评估 |
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
    "prettier": "^3.2.0"
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

---

## 3. 后端技术栈

### 3.1 核心依赖

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6

# NLP 相关
scikit-learn==1.4.0
jieba==0.42.1
numpy==1.26.3

# 密码强度检测
zxcvbn==4.4.2

# 敏感信息检测
regex==2023.12.25
```

### 3.2 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models/
│   │   ├── __init__.py
│   │   └── detection.py     # Pydantic 模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── detection.py     # 请求/响应模型
│   ├── routers/
│   │   ├── __init__.py
│   │   └── detection.py     # API 路由
│   ├── services/
│   │   ├── __init__.py
│   │   ├── detector.py      # 检测服务
│   │   └── history.py       # 历史记录服务
│   └── detectors/
│       ├── __init__.py
│       ├── phishing.py      # 钓鱼邮件检测（NLP）
│       ├── weak_password.py # 弱密码检测
│       └── sensitive_info.py # 敏感信息泄露检测
├── tests/
│   ├── __init__.py
│   └── test_detectors.py
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
    input_content TEXT NOT NULL,       -- 输入内容
    detection_type TEXT NOT NULL,      -- 'phishing', 'weak_password', 'sensitive_info'
    risk_level TEXT NOT NULL,          -- 'high', 'medium', 'low', 'safe'
    result_detail TEXT,                -- 详细检测结果（JSON格式）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_created_at ON detection_history(created_at DESC);
CREATE INDEX idx_detection_type ON detection_history(detection_type);
```

---

## 5. API 设计

### 5.1 接口列表

| 方法 | 路径 | 描述 |
|-----|------|------|
| POST | /api/detect/text | 文本内容检测（钓鱼邮件/弱密码/敏感信息） |
| GET | /api/history | 获取检测历史 |
| DELETE | /api/history/{id} | 删除单条历史 |
| DELETE | /api/history | 清空所有历史 |

### 5.2 请求/响应示例

**POST /api/detect/text**

```json
// Request
{
  "content": "您的账户存在异常，请立即点击链接验证身份...",
  "detection_type": "phishing"  // 可选: phishing, weak_password, sensitive_info
}

// Response (钓鱼邮件检测)
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

// Response (弱密码检测)
{
  "success": true,
  "result": {
    "type": "weak_password",
    "risk_level": "high",
    "score": 2,
    "score_max": 4,
    "feedback": [
      "密码太短",
      "缺少数字和特殊字符"
    ],
    "suggestions": [
      "使用至少8位密码",
      "包含大小写字母、数字和特殊字符"
    ]
  }
}

// Response (敏感信息检测)
{
  "success": true,
  "result": {
    "type": "sensitive_info",
    "risk_level": "high",
    "findings": [
      {
        "type": "api_key",
        "value": "sk-*******",
        "position": "第15-30字符"
      },
      {
        "type": "password",
        "value": "******",
        "position": "第50-60字符"
      }
    ],
    "suggestions": [
      "使用环境变量代替硬编码密钥",
      "敏感信息不应提交到版本控制系统"
    ]
  }
}
```

---

## 6. Docker 配置

### 6.1 Dockerfile (后端)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Dockerfile (前端)

```dockerfile
FROM node:20-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 6.3 docker-compose.yml

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
      - DATABASE_URL=sqlite:///app/data/detections.db

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

## 7. 开发工具推荐

| 用途 | 工具 |
|-----|------|
| API 测试 | Postman / Bruno |
| 数据库管理 | SQLite Browser |
| 代码格式化 | Prettier + Black |
| 版本控制 | Git |

---

## 8. 版本锁定建议

所有依赖版本在 `requirements.txt` 和 `package.json` 中锁定具体版本，避免因依赖更新导致兼容性问题。

生产环境使用 `npm ci` 和 `pip install -r requirements.txt --no-deps` 确保一致性。
