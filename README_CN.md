# OpenAI API 转发服务

一个轻量级的 OpenAI 兼容 API 转发服务，可将请求代理到另一个 OpenAI 兼容的 API 端点。

## 功能特性

- ✅ 完全兼容 OpenAI API 规范
- ✅ 支持聊天补全 (`/v1/chat/completions`)
- ✅ 支持文本补全 (`/v1/completions`)
- ✅ 支持模型列表查询 (`/v1/models`)
- ✅ 自动转发所有其他 OpenAI API 端点
- ✅ 透传所有请求参数（包括 `extra_body`）
- ✅ 错误处理与状态码转发
- ✅ 基于环境变量的配置管理

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制示例配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置目标 API：

```env
# 目标 API 配置
TARGET_API_BASE_URL=https://api.openai.com/v1
TARGET_API_KEY=your_openai_api_key_here

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### 3. 启动服务

```bash
python run.py
```

或直接运行：

```bash
python main.py
```

服务将在 `http://0.0.0.0:8000` 启动。

## API 使用示例

### 获取模型列表

```bash
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer any_key"
```

### 聊天补全

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any_key" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 文本补全

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any_key" \
  -d '{
    "model": "text-davinci-003",
    "prompt": "Say this is a test"
  }'
```

## 测试

项目内置了 `test_api.py` 测试脚本，可快速验证转发服务是否正常工作。

### 配置

编辑 `test_api.py` 顶部的参数，使其与你的环境匹配：

```python
openai_api_key = "EMPTY"          # 转发服务的 API Key（任意字符串即可）
openai_api_base = "http://localhost:8000/v1"  # 转发服务地址

MODEL_PATH = 'hunyuan-a13b'       # 要测试的模型名称

temperature = 0.05
top_p = 0.1
repetition_penalty = 1.05
max_tokens = 128
```

### 运行测试

```bash
python test_api.py
```

脚本会发送一条包含 `"hello"` 消息的聊天补全请求，并打印模型的回复。额外参数（如 `repetition_penalty`）通过 `extra_body` 传递，用于验证完整的参数透传功能。

### 预期输出

```
ChatCompletionMessage(content='Hello! How can I assist you today?', role='assistant', ...)
```

> **注意：** 客户端设置了 `timeout=60.0`。如果后端模型响应较慢，请适当增大该值。

## 配置说明

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TARGET_API_BASE_URL` | `https://api.openai.com/v1` | 目标 API 的基础 URL |
| `TARGET_API_KEY` | — | 目标 API 的认证密钥 |
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8000` | 服务监听端口 |
| `DEBUG` | `false` | 是否开启调试模式 |
| `PRINT_PAYLOAD` | `false` | 是否将请求 payload 打印到标准输出（设为 `1`、`true` 或 `yes` 开启） |

## 支持的端点

- `GET /v1/models` — 获取模型列表
- `POST /v1/chat/completions` — 聊天补全
- `POST /v1/completions` — 文本补全
- 所有其他 `/v1/*` 端点均自动转发

## 项目结构

```
openai_api_forwarder/
├── main.py          # 核心转发服务
├── run.py           # 启动脚本
├── test_api.py      # 测试脚本
├── requirements.txt # Python 依赖
├── .env.example     # 环境配置示例
├── README.md        # 文档（英文）
└── README_CN.md     # 文档（中文）
```

## 许可证

MIT License
