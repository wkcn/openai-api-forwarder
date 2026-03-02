# OpenAI API Forwarder

A lightweight OpenAI-compatible API forwarding service that proxies requests to another OpenAI-compatible API endpoint.

## Features

- ✅ Fully compatible with the OpenAI API specification
- ✅ Supports chat completions (`/v1/chat/completions`)
- ✅ Supports text completions (`/v1/completions`)
- ✅ Supports model listing (`/v1/models`)
- ✅ Forwards all other OpenAI API endpoints automatically
- ✅ Passes through all request parameters (including `extra_body`)
- ✅ Error handling and status code forwarding
- ✅ Environment variable based configuration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example config file:

```bash
cp .env.example .env
```

Edit `.env` to set your target API:

```env
# Target API configuration
TARGET_API_BASE_URL=https://api.openai.com/v1
TARGET_API_KEY=your_openai_api_key_here

# Server configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### 3. Start the Service

```bash
python run.py
```

Or run directly:

```bash
python main.py
```

The service will be available at `http://0.0.0.0:8000`.

## API Usage Examples

### List Models

```bash
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer any_key"
```

### Chat Completion

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any_key" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Text Completion

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any_key" \
  -d '{
    "model": "text-davinci-003",
    "prompt": "Say this is a test"
  }'
```

## Testing

A ready-to-use test script `test_api.py` is included to quickly verify the forwarding service.

### Configuration

Edit the top of `test_api.py` to match your setup:

```python
openai_api_key = "EMPTY"          # API key for the forwarder (can be any string)
openai_api_base = "http://localhost:8000/v1"  # Forwarder service address

MODEL_PATH = 'hunyuan-a13b'       # Model name to test with

temperature = 0.05
top_p = 0.1
repetition_penalty = 1.05
max_tokens = 128
```

### Run the Test

```bash
python test_api.py
```

The script sends a chat completion request with a simple `"hello"` message and prints the model's response. Extra parameters (e.g. `repetition_penalty`) are passed via `extra_body` to verify full parameter forwarding.

### Expected Output

```
ChatCompletionMessage(content='Hello! How can I assist you today?', role='assistant', ...)
```

> **Note:** A `timeout=60.0` is set on the client. If the backend model is slow to respond, increase this value accordingly.

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `TARGET_API_BASE_URL` | `https://api.openai.com/v1` | Target API base URL |
| `TARGET_API_KEY` | — | Authentication key for the target API |
| `HOST` | `0.0.0.0` | Server listen address |
| `PORT` | `8000` | Server listen port |
| `DEBUG` | `false` | Enable debug mode |
| `PRINT_PAYLOAD` | `false` | Print request payload to stdout (set to `1`, `true`, or `yes` to enable) |
| `PRINT_RESPONSE` | `false` | Print response to stdout (set to `1`, `true`, or `yes` to enable) |

## Supported Endpoints

- `GET /v1/models` — List available models
- `POST /v1/chat/completions` — Chat completion
- `POST /v1/completions` — Text completion
- All other `/v1/*` endpoints are forwarded automatically

## Project Structure

```
openai_api_forwarder/
├── main.py          # Core forwarding service
├── run.py           # Startup script
├── test_api.py      # Test script
├── requirements.txt # Python dependencies
├── .env.example     # Example environment config
├── README.md        # Documentation (English)
└── README_CN.md     # Documentation (Chinese)
```

## License

MIT License
