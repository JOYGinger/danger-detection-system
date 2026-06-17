# \# Danger Detection System 危险检测系统

一个基于 FastAPI \+ React 的多维度危险内容检测系统，支持钓鱼邮件、弱密码、恶意链接、敏感信息等多种检测类型。

> **外部链接探测批注（实测访问结果）**
> 
> - `https://pypi.tuna.tsinghua.edu.cn/simple`：网页解析失败，不支持网页类型，pip镜像源可正常调用，页面无法可视化解析
> 
> - `http://127.0.0.1:8000` / `http://127.0.0.1:8000/health` / `http://127.0.0.1:8000/docs` / `http://127.0.0.1:3000`：URL校验异常，本地前后端服务未启动/端口无监听，无法访问
> 
> - `http://bank-verify.fake/secure/login`：网页解析失败，伪造银行域名，恶意钓鱼站点
> 
> - `http://fake-bank.com/verify`：访问成功，高风险站点，内嵌博彩色情导流、虚假体育平台、违规博彩APP推广，夹带企业无关引流信息，判定恶意钓鱼违规站点
> 
> 

---

## 目录


- [功能特性](https://www.doubao.cn)

- [技术栈](https://www.doubao.cn)

- [项目结构](https://www.doubao.cn)

- [快速开始](https://www.doubao.cn)

- [配置说明](https://www.doubao.cn)

- [API 接口](https://www.doubao.cn)

- [常见问题](https://www.doubao.cn)

- [许可证](https://www.doubao.cn)

---

## 功能特性


|<br>功能<br>|<br>说明<br>|
|---|---|
|<br> **多类型检测**|<br>支持钓鱼邮件、弱密码、恶意链接、敏感信息等多种检测<br>|
|<br> **风险评级**|<br>提供风险等级（高/中/低）和置信度评分<br>|
|<br> **历史记录**|<br>保存所有检测记录，支持查看详情、删除和清空<br>|
|<br> **数据加密**|<br>敏感数据使用 Fernet 对称加密存储<br>|
|<br> **现代化界面**|<br>基于 React \+ Vite \+ TailwindCSS 构建<br>|
|<br> **响应式设计**|<br>适配桌面和移动设备<br>|

---

## 技术栈


### 后端

|<br>技术<br>|<br>版本<br>|<br>用途<br>|
|---|---|---|
|<br>Python|<br>3\.12 / 3\.13<br>|<br>运行环境<br>|
|<br>FastAPI<br>|<br>0\.115\.0<br>|<br>Web 框架<br>|
|<br>SQLAlchemy<br>|<br>2\.0\.36<br>|<br>ORM 数据库操作<br>|
|<br>scikit\-learn<br>|<br>1\.5\.2<br>|<br>机器学习检测模型<br>|
|<br>cryptography<br>|<br>43\.0\.0<br>|<br>数据加密<br>|
|zxcvbn\-python<br>|<br>4\.4\.2<br>|<br>密码强度检测<br>|
|<br>jieba<br>|<br>0\.42\.1<br>|<br>中文分词<br>|
|<br>pandas<br>|<br>2\.2\.2<br>|<br>数据处理|
|<br>numpy<br>|2\.1\.0<br>|<br>数值计算<br>|

### 前端


|<br>技术<br>|<br>版本<br>|<br>用途<br>|
|---|---|---|
|<br>React<br>|<br>18\.x<br>|<br>UI 框架<br>|
|<br>TypeScript<br>|<br>5\.x<br>|<br>类型安全<br>|
|<br>Vite<br>|<br>5\.x<br>|<br>构建工具<br>|
|<br>TailwindCSS<br>|<br>3\.x<br>|<br>CSS 框架<br>|
|<br>Axios<br>|<br>\-<br>|<br>HTTP 客户端<br>|

---

## 项目结构


```text
danger-detection-system-main/
├── backend/                         # 后端服务
│   ├── app/
│   │   ├── api/                     # API 接口定义
│   │   ├── detectors/               # 检测器实现
│   │   │   ├── phishing_email.py    # 钓鱼邮件检测
│   │   │   ├── weak_password.py     # 弱密码检测
│   │   │   ├── malicious_link.py    # 恶意链接检测
│   │   │   └── sensitive_info.py    # 敏感信息检测
│   │   ├── ml/                      # 机器学习模型
│   │   │   └── phishing_model.py    # 钓鱼邮件分类模型
│   │   ├── models/                  # 数据库模型
│   │   │   └── history.py           # 历史记录模型
│   │   ├── routers/                 # 路由定义
│   │   │   ├── detection.py         # 检测路由
│   │   │   └── history.py           # 历史记录路由
│   │   ├── services/                # 业务逻辑层
│   │   │   └── history.py           # 历史记录服务
│   │   ├── utils/                   # 工具函数
│   │   │   └── crypto.py            # 加密工具
│   │   └── main.py                  # 应用入口
│   ├── data/                        # 数据库文件（自动生成）
│   │   └── history.db               # SQLite 数据库
│   ├── .env                         # 环境变量配置
│   ├── requirements.txt             # Python 依赖列表
│   └── .venv/                       # Python 虚拟环境
├── frontend/                        # 前端应用
│   ├── src/
│   │   ├── api/                     # API 调用封装
│   │   │   └── index.ts             # API 请求函数
│   │   ├── components/              # React 组件
│   │   │   ├── DetectionForm.tsx    # 检测表单
│   │   │   ├── ResultCard.tsx       # 结果展示
│   │   │   └── HistoryList.tsx      # 历史列表
│   │   ├── pages/                   # 页面组件
│   │   │   ├── Detection.tsx        # 检测页面
│   │   │   └── History.tsx          # 历史页面
│   │   ├── utils/                   # 工具函数
│   │   └── main.tsx                 # 应用入口
│   ├── public/                      # 静态资源
│   ├── index.html                   # HTML 模板
│   ├── package.json                 # npm 依赖
│   ├── vite.config.ts               # Vite 配置
│   └── tailwind.config.js           # Tailwind 配置
└── README.md                        # 项目文档

```

---

## 快速开始


### 前提条件


- Windows 操作系统


- Python 3\.12 或 3\.13 已安装


- Node\.js \(推荐 v18\+\) 已安装


- npm 包管理器已安装


### 第一步：克隆项目


```bash
git clone <repository-url>
cd danger-detection-system-main
```

### 第二步：启动后端


#### 2\.1 进入后端目录


```bash
cd backend
```

#### 2\.2 创建 Python 虚拟环境


```bash
py -3.12 -m venv .venv
```

#### 2\.3 激活虚拟环境


Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

 提示：如果遇到执行策略限制，先执行：

```bash
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

激活成功后，命令行前会出现 \(\.venv\) 前缀。

#### 2\.4 生成加密密钥


```bash
py -3.12 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

示例输出：

```text
Rc2m2O0Sf6OPPZHci6G_bvSjifAVZPvehJmqL5jkijU=
```

复制并保存此密钥，后续步骤需要使用。

#### 2\.5 创建 \.env 配置文件


```bash
# 创建 .env 文件并写入密钥
@"
ENCRYPTION_KEY=你生成的密钥
"@ | Out-File -FilePath .env -Encoding utf8

# 验证文件内容
Get-Content .env
```

预期输出：

```text
ENCRYPTION_KEY=Rc2m2O0Sf6OPPZHci6G_bvSjifAVZPvehJmqL5jkijU=
```

#### 2\.6 安装 Python 依赖


```bash
pip install -r requirements.txt
```

提示：如果安装速度慢，可使用国内清华镜像源（镜像站点仅pip拉取可用，页面无法可视化解析）：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 2\.7 启动后端服务


```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --env-file .env
```

验证后端启动成功：

|<br>检查项<br>|<br>地址<br>|<br>预期结果<br>|
|---|---|---|
|<br>健康检查<br>|<br>http://127\.0\.0\.1:8000/health<br>|<br>\{"status":"ok"\}<br>|
|<br>API 文档<br>|<br>http://127\.0\.0\.1:8000/docs<br>|<br>Swagger UI 页面<br>|

重要：保持此终端窗口打开，不要关闭！未启动时本地8000端口全部访问报错。

### 第三步：启动前端


在新的 PowerShell 窗口中执行以下命令

#### 3\.1 进入前端目录


```bash
cd frontend
```

#### 3\.2 安装前端依赖


```bash
npm install
```

如果遇到权限错误 EPERM：

方案一：清除缓存

```bash
npm cache clean --force
npm install
```

方案二：以管理员身份运行 PowerShell

```bash
# 右键点击 PowerShell → 以管理员身份运行
```

#### 3\.3 启动前端开发服务器


```bash
npm run dev -- --host 127.0.0.1 --port 3000
```

验证前端启动成功：访问：http://127\.0\.0\.1:3000，看到项目主界面即可。

重要：保持此终端窗口打开，不要关闭！未启动时本地3000端口访问报错。

### 第四步：功能验证


|<br>序号|<br>测试项<br>|<br>操作步骤<br>|<br>预期结果<br>|
|---|---|---|---|
|<br>1<br>|<br>检测功能<br>|<br>输入测试文本 → 选择"钓鱼邮件检测" → 点击"开始检测"<br>|<br>显示风险等级和置信度<br>|
|<br>2<br>|<br>历史记录<br>|<br>点击顶部"历史"导航<br>|<br>显示所有检测记录<br>|
|<br>3<br>|<br>查看详情<br>|<br>点击某条记录<br>|<br>显示完整检测详情<br>|
|<br>4<br>|<br>删除记录<br>|<br>点击删除按钮<br>|<br>记录被删除<br>|
|<br>5<br>|<br>清空所有|<br>点击"清空所有"按钮<br>|<br>列表变为空态<br>|

推荐测试文本（已实测判定为高风险）：

```text
尊敬的客户，您的银行账户存在异常交易，请立即点击以下链接进行验证，否则账户将被冻结：
http://bank-verify.fake/secure/login
```

---

## 配置说明


### 环境变量 \(\.env\)


|<br>变量名<br>|<br>类型|<br>必填<br>|<br>说明<br>|<br>示例<br>|
|---|---|---|---|---|
|<br>ENCRYPTION\_KEY<br>|<br>string<br>|<br>✅<br>|<br>Fernet 对称加密密钥<br>|<br>Rc2m2O0Sf6OPPZHci6G\_\.\.\.<br>|

### 端口配置


|<br>服务<br>|<br>默认端口<br>|<br>配置文件<br>|<br>修改方式<br>|
|---|---|---|---|
|<br>后端 API<br>|<br>8000<br>|<br>启动命令<br>|<br>\-\-port 8001<br>|
|<br>前端开发服务器<br>|<br>3000<br>|<br>vite\.config\.ts<br>|<br>修改 port: 3000<br>|

### 代理配置


前端代理配置位于 frontend/vite\.config\.ts：

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // 后端地址
        changeOrigin: true,
      },
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
```

---

## API 接口


### 接口列表

|<br>方法<br>|<br>路径<br>|<br>说明<br>|<br>请求体<br>|
|---|---|---|---|
|<br>POST<br>|<br>/api/detect/text<br>|文本检测<br>|<br>\{"content": "待检测文本"\}<br>|
|<br>GET<br>|<br>/api/history<br>|<br>获取历史记录<br>|<br>\-<br>|
|<br>GET<br>|<br>/api/history/\{id\}<br>|<br>获取单条记录<br>|<br>\-<br>|
|<br>DELETE<br>|/api/history/\{id\}<br>|<br>删除记录<br>|<br>\-<br>|
|<br>DELETE<br>|<br>/api/history/all<br>|<br>清空所有记录<br>|<br>\-<br>|
|<br>GET<br>|<br>/health<br>|<br>健康检查<br>|<br>\-<br>|
|<br>GET<br>|<br>/docs<br>|<br>Swagger API 文档<br>|<br>\-<br>|

### 检测请求示例


```http
POST /api/detect/text HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "content": "您的账户存在风险，请立即点击链接验证：http://fake-bank.com/verify"
}
```

### 检测响应示例


```json
{
  "overall_risk": "高风险",
  "results": {
    "phishing_email": {
      "risk": "高风险",
      "confidence": 0.95,
      "suggestions": [
        "不要点击可疑链接",
        "验证发件人地址",
        "不要提供个人敏感信息"
      ],
      "details": {
        "urls_found": ["http://fake-bank.com/verify"],
        "suspicious_keywords": ["验证", "冻结", "立即"]
      }
    }
  }
}
```

### 历史记录响应示例


```json
{
  "items": [
    {
      "id": 1,
      "content": "您的账户存在风险...",
      "detection_type": "all",
      "overall_risk": "高风险",
      "results": {
        "phishing_email": {
          "risk": "高风险",
          "confidence": 0.95
        }
      },
      "created_at": "2026-06-17T11:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

---

## 常见问题


### 后端问题


|<br>问题<br>|<br>原因<br>|<br>解决方案<br>|
|---|---|---|
|<br>ENCRYPTION\_KEY环境变量未设置<br>|<br>\.env 文件未正确加载<br>|<br>使用 \-\-env\-file \.env 启动<br>|
|<br>ModuleNotFoundError: No module named 'xxx'<br>|<br>依赖未安装<br>|pip install \-r requirements\.txt<br>|
|<br>端口 8000 被占用/访问报错<br>|<br>后端未启动/其他程序占用端口<br>|<br>启动后端服务，或换用其他端口：\-\-port 8001<br>|
|<br>数据库错误<br>|<br>data/ 目录不存在<br>|<br>自动创建，检查目录权限<br>|

### 前端问题


|<br>问题<br>|<br>原因<br>|<br>解决方案<br>|
|---|---|---|
|<br>ECONNREFUSED<br>|<br>后端未启动或端口不匹配<br>|<br>检查后端是否运行，确认 vite\.config\.ts 代理端口<br>|
|<br>EPERM: operation not permitted<br>|<br>npm 权限不足<br>|<br>以管理员身份运行，或清除缓存<br>|
|<br>页面空白<br>|<br>依赖未正确安装<br>|<br>删除 node\_modules，重新 npm install<br>|
|<br>跨域错误 \(CORS\)<br>|<br>后端 CORS 配置问题<br>|<br>后端已配置 CORS，重启后端即可<br>|

### PowerShell 问题


|<br>问题<br>|<br>解决方案<br>|
|---|---|
|<br>脚本执行限制<br>|<br>Set\-ExecutionPolicy \-Scope CurrentUser RemoteSigned<br>|
|<br>路径包含空格<br>|<br>使用双引号包裹路径：cd "D:\\My Project"<br>|

### 链接探测专项问题


|<br>访问地址<br>|<br>异常原因<br>|<br>风险判定<br>|
|---|---|---|
|<br>清华pip镜像源<br>|<br>站点非可视化网页，解析器不兼容<br>|<br>安全可信，仅页面解析失败<br>|
|<br>fake银行域名<br>|<br>伪造域名，无合规备案<br>|<br>高风险钓鱼站点<br>|
|<br>本地127\.0\.0\.1端口<br>|<br>前后端服务未启动监听<br>|<br>本地内网地址，无外网风险<br>|

---

## 许可证


MIT License

Copyright \(c\) 2024

```text
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
