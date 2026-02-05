import os
import asyncio
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from litellm import acompletion

THINKERS = [
    {"name": "groq", "model": "llama-3.3-70b-versatile", "weight": 0.40},
    {"name": "gemini", "model": "gemini-2.0-flash-exp", "weight": 0.30},
    {"name": "mistral", "model": "mistral-large-latest", "weight": 0.20},
    {"name": "ollama", "model": "llama3.1:7b", "weight": 0.10}
]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def think_single(thinker: Dict, query: str) -> Optional[Dict]:
    try:
        os.environ[f"{thinker['name'].upper()}_API_KEY"] = os.getenv(f"{thinker['name'].upper()}_API_KEY", "")
        response = await acompletion(
            model=thinker["model"],
            messages=[{"role": "user", "content": f"Deep research answer only: {query}"}],
            max_tokens=500,
            temperature=0.1
        )
        return {
            "thinker": thinker["name"],
            "answer": response.choices[0].message.content,
            "confidence": 0.8,
            "weight": thinker["weight"],
            "success": True
        }
    except Exception as e:
        print(f"{thinker['name']} failed: {e}")
        return None
async def parallel_thinkers(query: str) -> List[Dict]:
    tasks = [think_single(t, query) for t in THINKERS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if isinstance(r, dict) and r and r.get("success")]
