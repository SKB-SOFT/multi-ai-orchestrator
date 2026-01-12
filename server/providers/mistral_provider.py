import asyncio
import aiohttp
import json
from typing import Dict, Any, List
import time
from .base_provider import BaseProvider

class MistralProvider(BaseProvider):
    """
    Mistral AI Provider - Open models with strong reasoning
    Free tier: 1 req/sec, 500K tokens/month
    No credit card required
    
    Docs: https://docs.mistral.ai/capabilities/function_calling/
    """
    
    def __init__(self, api_key: str, model_name: str = "mistral-large-latest"):
        super().__init__(api_key, model_name)
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
    
    async def query(self, prompt: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Query Mistral API with OpenAI-compatible interface.
        """
        start_time = time.time()
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Provide concise, accurate responses."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        response_text = data["choices"][0]["message"]["content"]
                        
                        # Get token count
                        token_count = 0
                        if "usage" in data:
                            token_count = (data["usage"].get("prompt_tokens", 0) + 
                                         data["usage"].get("completion_tokens", 0))
                        
                        return self.format_response(
                            response_text=response_text,
                            response_time_ms=response_time_ms,
                            token_count=token_count if token_count > 0 else len(response_text.split())
                        )
                    else:
                        error_text = await response.text()
                        return self.format_error(
                            error_message=f"HTTP {response.status}: {error_text[:100]}",
                            response_time_ms=response_time_ms
                        )
        
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            return self.format_error(
                error_message="Request timeout (30s)",
                response_time_ms=response_time_ms
            )
        
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return self.format_error(
                error_message=f"Mistral Error: {str(e)[:100]}",
                response_time_ms=response_time_ms
            )
    
    async def validate_key(self) -> bool:
        """
        Validate Mistral API key.
        """
        try:
            result = await self.query("Hello", timeout=10)
            return result["status"] == "success"
        except Exception:
            return False
    
    @staticmethod
    def get_available_models() -> List[str]:
        """
        Return list of available Mistral models.
        """
        return [
            "mistral-large-latest",  # Most capable
            "mistral-medium-latest",
            "mistral-small-latest",  # Fastest, free tier friendly
            "open-mistral-7b",       # Open source variant
            "open-mixtral-8x7b",     # More capable open source
        ]
