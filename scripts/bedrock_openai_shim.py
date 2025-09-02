# Minimal OpenAI-compatible → Bedrock InvokeModel shim
import json
import os
import time
from typing import List, Optional

import boto3
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")
brt = boto3.client("bedrock-runtime", region_name=REGION)

app = FastAPI()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.2


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
