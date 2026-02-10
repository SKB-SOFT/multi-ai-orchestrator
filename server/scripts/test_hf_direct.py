import asyncio
import aiohttp
import os
from dotenv import load_dotenv

async def test_hf():
    load_dotenv("server/.env")
    key = os.getenv("HUGGINGFACE_API_KEY_1")
    model = "gpt2"
    url = f"https://router.huggingface.co/hf-inference/v1/chat/completions"
    
    print(f"Testing HF with key: {key[:10]}... and OpenAI-compatible URL")
    
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt2",
        "messages": [{"role": "user", "content": "Hello"}]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                print(f"Status: {resp.status}")
                text = await resp.text()
                print(f"Response: {text[:200]}")
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_hf())
