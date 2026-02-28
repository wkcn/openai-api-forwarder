import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
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

if not TARGET_API_KEY:
    raise ValueError("TARGET_API_KEY environment variable is required")

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[list] = None
    stream: Optional[bool] = False

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[list] = None
    stream: Optional[bool] = False

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
async def create_chat_completion(request: ChatCompletionRequest):
    """创建聊天补全"""
    headers = {
        "Authorization": f"Bearer {TARGET_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = request.dict(exclude_none=True)

    if PRINT_PAYLOAD:
        print("[chat/completions] Payload:", json.dumps(payload, indent=2, ensure_ascii=False))

    if request.stream:
        async def stream_generator():
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
                        yield chunk
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
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=response.status_code, detail=f"Target API error: {str(e)}")

@app.post("/v1/completions")
async def create_completion(request: CompletionRequest):
    """创建文本补全"""
    headers = {
        "Authorization": f"Bearer {TARGET_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = request.dict(exclude_none=True)

    if PRINT_PAYLOAD:
        print("[completions] Payload:", json.dumps(payload, indent=2, ensure_ascii=False))

    if request.stream:
        async def stream_generator():
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
                        yield chunk
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
            return response.json()
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
