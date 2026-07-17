import requests
from src.core.config import settings
from src.core.observability import token_counter
from src.core.logger import logger

class LLMClient:
    def __init__(self):
        self.provider = settings.llm_provider
        self.ollama_url = settings.ollama_url
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_api_key)
        elif self.provider == "groq":
            from openai import OpenAI
            self.client = OpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        if self.provider == "ollama":
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": "llama3",
                        "prompt": f"{system_prompt}\n\n{prompt}",
                        "stream": False
                    },
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                prompt_tokens = data.get("prompt_eval_count", len(prompt.split()))
                completion_tokens = data.get("eval_count", 0)
                
                token_counter.add(prompt_tokens, {"model_name": "ollama", "token_type": "prompt"})
                token_counter.add(completion_tokens, {"model_name": "ollama", "token_type": "completion"})
                
                return data.get("response", "")
            except Exception as e:
                logger.error("ollama_generation_error", error=str(e))
                return "Error generating response from local LLM."
                
        elif self.provider in ["openai", "groq"]:
            model_name = "llama3-8b-8192" if self.provider == "groq" else "gpt-3.5-turbo"
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            
            usage = response.usage
            if usage:
                token_counter.add(usage.prompt_tokens, {"model_name": model_name, "token_type": "prompt"})
                token_counter.add(usage.completion_tokens, {"model_name": model_name, "token_type": "completion"})
                
            return response.choices[0].message.content

llm_client = LLMClient()
