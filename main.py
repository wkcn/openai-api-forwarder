import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="OpenAI API Forwarder",
    description="A service that forwards OpenAI-compatible API requests to another OpenAI-compatible API",
    version="1.0.0"
)

# Configuration
TARGET_API_BASE_URL = os.getenv("TARGET_API_BASE_URL", "https://api.openai.com/v1")
TARGET_API_KEY = os.getenv("TARGET_API_KEY")
PRINT_PAYLOAD = os.getenv("PRINT_PAYLOAD", "").lower() in ("1", "true", "yes")
PRINT_RESPONSE = os.getenv("PRINT_RESPONSE", "").lower() in ("1", "true", "yes")

if not TARGET_API_KEY:
    raise ValueError("TARGET_API_KEY environment variable is required")

def parse_stream_response(raw_bytes: bytes) -> str:
    """Parse SSE stream bytes, concatenate content and finish_reason for printing."""
    full_content = []
    finish_reason = None
    text = raw_bytes.decode("utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data_str = line[len("data:"):].strip()
        if data_str == "[DONE]":
            continue
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError:
            continue
        choices = data.get("choices", [])
        for choice in choices:
            delta = choice.get("delta", {})
            content = delta.get("content", "")
            if content:
                full_content.append(content)
            fr = choice.get("finish_reason")
            if fr:
                finish_reason = fr
    result = "".join(full_content)
    if finish_reason:
        result += f" [finish_reason: {finish_reason}]"
    return result

@app.get("/")
async def root():
    return {"message": "OpenAI API Forwarder is running"}

@app.get("/v1/models")
async def list_models():
    """获取可用的模型列表"""
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {TARGET_API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await client.get(f"{TARGET_API_BASE_URL}/models", headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=response.status_code, detail=f"Target API error: {str(e)}")

@app.post("/v1/chat/completions")
async def create_chat_completion(request: Request):
    """Forward chat completion requests"""
    headers = {
        "Authorization": f"Bearer {TARGET_API_KEY}",
        "Content-Type": "application/json"
    }

    body = await request.body()
    payload = json.loads(body) if body else {}

    if PRINT_PAYLOAD:
        print("[chat/completions] Payload:", json.dumps(payload, ensure_ascii=False))

    stream = payload.get("stream", False)

    if stream:
        async def stream_generator():
            chunks = []
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{TARGET_API_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                ) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes():
                        if PRINT_RESPONSE:
                            chunks.append(chunk)
                        yield chunk
            if PRINT_RESPONSE:
                parsed = parse_stream_response(b"".join(chunks))
                print("[chat/completions] Response (stream):", parsed)
        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TARGET_API_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            if PRINT_RESPONSE:
                print("[chat/completions] Response:", json.dumps(result, ensure_ascii=False))
            return result
        except httpx.HTTPError as e:
            raise HTTPException(status_code=response.status_code, detail=f"Target API error: {str(e)}")

@app.post("/v1/completions")
async def create_completion(request: Request):
    """Forward text completion requests"""
    headers = {
        "Authorization": f"Bearer {TARGET_API_KEY}",
        "Content-Type": "application/json"
    }

    body = await request.body()
    payload = json.loads(body) if body else {}

    if PRINT_PAYLOAD:
        print("[completions] Payload:", json.dumps(payload, ensure_ascii=False))

    stream = payload.get("stream", False)

    if stream:
        async def stream_generator():
            chunks = []
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{TARGET_API_BASE_URL}/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                ) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes():
                        if PRINT_RESPONSE:
                            chunks.append(chunk)
                        yield chunk
            if PRINT_RESPONSE:
                parsed = parse_stream_response(b"".join(chunks))
                print("[completions] Response (stream):", parsed)
        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TARGET_API_BASE_URL}/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            if PRINT_RESPONSE:
                print("[completions] Response:", json.dumps(result, ensure_ascii=False))
            return result
        except httpx.HTTPError as e:
            raise HTTPException(status_code=response.status_code, detail=f"Target API error: {str(e)}")

@app.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path: str):
    """捕获所有其他OpenAI API端点并转发"""
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {TARGET_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 获取请求体
        body = await request.body()
        
        try:
            json_body = json.loads(body) if body else None
        except json.JSONDecodeError:
            json_body = None
        
        target_url = f"{TARGET_API_BASE_URL}/{path}"
        
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                json=json_body,
                params=request.query_params,
                timeout=60.0
            )
            response.raise_for_status()
            
            # 返回原始响应
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.HTTPError as e:
            raise HTTPException(status_code=response.status_code, detail=f"Target API error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
