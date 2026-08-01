import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

@dataclass
class AgentMessage:
    role: str
    content: str

@dataclass
class BaseAgent:
    name: str
    system_prompt: str

    def get_client(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            from openai import OpenAI
            return OpenAI(api_key=api_key)
        except Exception as e:
            print(f"[OpenAI Client Init Error] {e}")
            return None

    def call_openai(
        self,
        messages: List[AgentMessage],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.4,
        max_tokens: int = 2500
    ) -> str:
        client = self.get_client()
        if not client:
            return (
                "⚠️ OPENAI_API_KEY is not set in environment or .env file.\n"
                "Please add your API key to .env file as: OPENAI_API_KEY=your_key_here"
            )

        try:
            payload = [{"role": m.role, "content": m.content} for m in messages]
            payload.insert(0, {"role": "system", "content": self.system_prompt})
            
            completion = client.chat.completions.create(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=payload
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"[BaseAgent OpenAI API Error] {e}")
            return f"⚠️ Error calling OpenAI API: {e}"
