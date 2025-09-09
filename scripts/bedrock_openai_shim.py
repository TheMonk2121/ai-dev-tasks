# Minimal OpenAI-compatible → Bedrock InvokeModel shim
import json
import os
import threading
import time
from typing import Optional

import boto3
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


class RateLimiter:
    def __init__(self, rps: float):
        self.min_interval = 1.0 / max(rps, 1e-6)
        self._next_ok = 0.0
        self._lock = threading.Lock()

    def wait(self):
        with self._lock:
            now = time.monotonic()
            wait = self._next_ok - now
            if wait > 0:
                time.sleep(wait)
            self._next_ok = max(self._next_ok, now) + self.min_interval


# Initialize rate limiter with conservative defaults
rate_limiter = RateLimiter(float(os.getenv("BEDROCK_MAX_RPS", "0.22")))

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")
brt = boto3.client("bedrock-runtime", region_name=REGION)

app = FastAPI()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    max_tokens: int | None = 512
    temperature: float | None = 0.2


@app.post("/v1/chat/completions")
def chat(req: ChatRequest):
    # naive role->text join; good enough for evaluation claims/checks
    text = []
    for m in req.messages:
        tag = m.role.upper()
        text.append(f"[{tag}]\n{m.content}")
    user_prompt = "\n".join(text)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": int(req.max_tokens or 512),
        "temperature": float(req.temperature or 0.2),
        "messages": [{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
    }

    t0 = time.time()

    # Apply rate limiting before Bedrock call
    rate_limiter.wait()

    out = brt.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )
    resp = json.loads(out["body"].read())
    content = ""
    for blk in resp.get("content", []):
        if blk.get("type") == "text":
            content += blk.get("text", "")

    usage = resp.get("usage", {})  # Bedrock returns input_tokens/output_tokens
    return {
        "id": f"shim-{int(t0)}",
        "object": "chat.completion",
        "model": req.model,
        "created": int(t0),
        "usage": {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        },
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", "8089")))
