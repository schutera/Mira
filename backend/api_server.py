from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_interface import query_gpt

app = FastAPI()

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str
    guardrails: bool = True  # Add guardrails as an optional field with default True

@app.post("/api/ask")
async def ask_gpt(req: PromptRequest):
    answer = query_gpt(req.prompt, guardrails=req.guardrails)
    return {"response": answer}