import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
import time
from .base_provider import BaseProvider

class HuggingFaceProvider(BaseProvider):
    def __init__(self, api_key: str, model_id: str = 'HuggingFaceH4/zephyr-7b-beta', api_keys: Optional[List[str]] = None):
        super().__init__(api_key, model_id, api_keys)
        self.model_id = model_id
        self.router_url = f'https://router.huggingface.co/hf-inference/models/{model_id}'
        self.legacy_url = f'https://api-inference.huggingface.co/models/{model_id}'
    
    async def query(self, prompt: str, timeout: int = 30) -> Dict[str, Any]:
        start_time = time.time()
        max_retries = 3
        backoff_ms = 100
        payload = {
            'inputs': prompt,
            'parameters': {'max_new_tokens': 512, 'temperature': 0.7, 'return_full_text': False},
            'options': {'wait_for_model': True, 'use_cache': True}
        }
        async with aiohttp.ClientSession() as session:
            for attempt in range(max_retries + 1):
                try:
                    headers = {'Authorization': f'Bearer {self.get_next_key()}'}
                    async def _attempt(url):
                        async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                            return resp, (time.time() - start_time) * 1000
                    response, response_time_ms = await _attempt(self.router_url)
                    if response.status in (404, 410):
                        response, response_time_ms = await _attempt(self.legacy_url)
                    if response.status == 200:
                        data = await response.json()
                        response_text = ''
                        if isinstance(data, list) and data:
                            response_text = data[0].get('generated_text') or data[0].get('summary_text', '')
                        elif isinstance(data, dict):
                            response_text = data.get('generated_text') or data.get('summary_text', '')
                        return self.format_response(response_text or str(data)[:500], response_time_ms)
                    elif response.status == 503 and attempt < max_retries:
                        await asyncio.sleep(backoff_ms / 1000.0)
                        backoff_ms = min(backoff_ms * 2, 500)
                        continue
                    else:
                        err_text = await response.text()
                        err_type = 'unauthorized' if response.status in (401, 403) else 'rate_limited' if response.status == 429 else 'provider_down' if response.status >= 500 else 'unknown'
                        return self.format_error(f'HTTP {response.status}: {err_text[:200]}', response_time_ms, err_type)
                except Exception as e:
                    if attempt < max_retries:
                        await asyncio.sleep(backoff_ms / 1000.0)
                        continue
                    return self.format_error(str(e), (time.time() - start_time) * 1000, 'provider_down')
    
    async def validate_key(self) -> bool:
        res = await self.query('Hi', timeout=10)
        return res['status'] == 'success'
