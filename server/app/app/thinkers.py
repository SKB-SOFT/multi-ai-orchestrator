import os
import asyncio
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import litellm  # Unified LLM interface

class Thinker:
    def __init__(self, name: str, model: str, weight: float):
        self.name = name
        self.model = model  
        self.weight = weight
        litellm.api_key = os.getenv(f"{name.upper()}_API_KEY")

async def think_single(model_info: Dict, query: str) -> Optional[Dict]:
    """Single thinker response with retry logic"""
    thinker_name, model, weight = model_info["name"], model_info["model"], model_info["weight"]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _call():
        try:
            response = await asyncio.to_thread(
                litellm.acompletion,
                model=model,
                messages=[{"role": "user", "content": f"Deep research answer only: {query}"}],
                max_tokens=500,
                temperature=0.1
            )
            return {
                "thinker": thinker_name,
                "answer": response.choices[0].message.content,
                "confidence": float(response.choices[0].message.metadata.get("confidence", 0.8)),
                "weight": weight,
                "success": True
            }
        except Exception as e:
            print(f"{thinker_name} failed: {e}")
            return None
    
    return await _call()

# 4 FREE THINKERS (V1)
THINKERS = [
    {"name": "groq", "model": "llama-3.3-70b-versatile", "weight": 0.40},
    {"name": "gemini", "model": "gemini-2.0-flash-exp", "weight": 0.30},
    {"name": "mistral", "model": "mistral-large-latest", "weight": 0.20},
    {"name": "ollama", "model": "llama3.1:7b", "weight": 0.10}
]

async def parallel_thinkers(query: str) -> List[Dict]:
    """All 4 thinkers think in parallel"""
    tasks = [think_single(thinker, query) for thinker in THINKERS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful = [r for r in results if isinstance(r, dict) and r and r.get("success")]
    return successful
