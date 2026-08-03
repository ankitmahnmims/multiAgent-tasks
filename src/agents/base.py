import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv(override=True)

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")

@dataclass
class AgentMessage:
    role: str
    content: str

@dataclass
class BaseAgent:
    name: str
    system_prompt: str

    def call_openai(
        self,
        messages: List[AgentMessage],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.4,
        max_tokens: int = 4000,
        response_json: bool = False
    ) -> str:
        load_dotenv(override=True)
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        # Priority 1: Gemini API
        if gemini_key and not gemini_key.startswith("your_"):
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=gemini_key)
                
                # Determine Gemini model name
                gemini_model = model if model.startswith("gemini-") else "gemini-2.5-flash"
                
                # Combine user messages into content string
                user_content = "\n\n".join([m.content for m in messages if m.role == "user"])

                config_args = {
                    "system_instruction": self.system_prompt,
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
                if response_json:
                    config_args["response_mime_type"] = "application/json"

                response = client.models.generate_content(
                    model=gemini_model,
                    contents=user_content,
                    config=types.GenerateContentConfig(**config_args)
                )
                return response.text.strip()
            except Exception as e:
                print(f"[{self.name} Gemini API Error] {e}")
                return f"⚠️ Error calling Gemini API: {e}"

        # Priority 2: OpenAI API
        elif openai_key and not openai_key.startswith("your_"):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                
                openai_model = model if not model.startswith("gemini-") else "gpt-4o-mini"
                payload = [{"role": m.role, "content": m.content} for m in messages]
                payload.insert(0, {"role": "system", "content": self.system_prompt})
                
                kwargs = {
                    "model": openai_model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "messages": payload
                }
                if response_json:
                    kwargs["response_format"] = {"type": "json_object"}

                completion = client.chat.completions.create(**kwargs)
                return completion.choices[0].message.content.strip()
            except Exception as e:
                print(f"[{self.name} OpenAI API Error] {e}")
                return f"⚠️ Error calling OpenAI API: {e}"

        else:
            return (
                "⚠️ No valid API Key found!\n"
                "Please add GEMINI_API_KEY=... or OPENAI_API_KEY=... in your .env file."
            )
