import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Load environment variables FIRST ---
load_dotenv()

# --- Read configuration (default to Groq) ---
PROVIDER = (os.getenv("PROVIDER", "groq") or "groq").strip().lower()
ALLOWED_ORIGINS = (os.getenv("ALLOWED_ORIGINS", "http://localhost:4200,http://localhost:4300") or "http://localhost:4200,http://localhost:4300").split(",")

if PROVIDER != "groq":
    # We only support Groq in this build to avoid falling back to OpenAI by mistake.
    raise RuntimeError(
        f"Unsupported PROVIDER={PROVIDER!r}. "
        "This backend is configured for Groq only. Set PROVIDER=groq in .env."
    )

# --- Groq (OpenAI‑compatible client) ---
from openai import OpenAI  # OpenAI SDK, pointing to Groq's base_url

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set. Add it to backend/.env.")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",  # Groq's OpenAI-compatible endpoint
)

app = FastAPI(title="Angular + FastAPI (Groq backend)", version="1.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str
    system: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512


class ChatResponse(BaseModel):
    output: str
    provider: str
    model: str


@app.get("/api/health")
def health():
    return {"status": "ok", "provider": PROVIDER, "model": GROQ_MODEL}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        messages = [
            {"role": "system", "content": req.system or "You are a helpful assistant."},
            {"role": "user", "content": req.prompt},
        ]
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=req.temperature or 0.7,
            max_tokens=req.max_tokens or 512,
        )
        output = completion.choices[0].message.content
        return ChatResponse(output=output, provider=PROVIDER, model=GROQ_MODEL)
    except Exception as e:
        msg = str(e)
        status = 500
        if "401" in msg:
            status = 401
        elif "429" in msg:
            status = 429
        elif "400" in msg:
            status = 400
        raise HTTPException(status_code=status, detail=f"groq error: {msg}")
