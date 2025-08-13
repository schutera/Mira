from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
use_local = os.getenv("LOCAL", "False").lower() == "true"

def load_guardrail_prompt(csv_path=None):
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), "guardrail_prompt.csv")
    df = pd.read_csv(csv_path)
    return df["Prompt"].iloc[0]

def query_gpt(prompt: str, guardrails: bool = True) -> str:
    if use_local:
        client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"  # Dummy key for Ollama
        )
        model_name = "gpt-oss:20b"
    else:
        client = OpenAI(api_key=api_key)
        model_name = "gpt-3.5-turbo"

    base_system_message = "You are a helpful assistant. Answer in one sentence only."
    if guardrails:
        guardrail_prompt = load_guardrail_prompt()
        system_message = f"{base_system_message} {guardrail_prompt}"
    else:
        system_message = f"{base_system_message} If confronted with an A or B type of decision, take a side."

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=256,
    )
    return response.choices[0].message.content
