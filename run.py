#!/usr/bin/env python3
"""
OpenAI API Forwarder - 启动脚本
"""

import os
import uvicorn
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🚀 Starting OpenAI API Forwarder...")
    print(f"📡 Target API: {os.getenv('TARGET_API_BASE_URL', 'https://api.openai.com/v1')}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )