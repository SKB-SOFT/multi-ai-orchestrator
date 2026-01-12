# Multi-AI Orchestrator - Server Setup Guide

## 🚀 Quick Start

This guide walks you through setting up all 6 free API providers and running the orchestrator.

---

## 📋 Prerequisites

- Python 3.10+
- `pip` package manager
- Internet connection

---

## 🔑 Step 1: Get API Keys for All 6 Providers

### 1️⃣ **Groq** (14.4K requests/day, fastest)

```bash
# Go to https://console.groq.com/keys
# Sign up (no credit card required)
# Copy your API key
```

**Env Variable:**
```bash
GROQ_API_KEY=gsk_YOUR_KEY_HERE
```

---

### 2️⃣ **Google Gemini** (15K tokens/day, web search)

```bash
# Go to https://aistudio.google.com/app/apikey
# Sign in with Google account
# Click "Create API Key"
# Copy the key starting with "AIza..."
```

**Env Variable:**
```bash
GEMINI_API_KEY=AIza_YOUR_KEY_HERE
```

---

### 3️⃣ **Mistral** (500K tokens/month, strong reasoning)

```bash
# Go to https://console.mistral.ai/api-tokens
# Sign up with email
# Create new API token
# Copy token
```

**Env Variable:**
```bash
MISTRAL_API_KEY=your_mistral_key_here
```

---

### 4️⃣ **Cerebras** (1M tokens/day (!), fastest)

```bash
# Go to https://cerebras.ai
# Sign up (no credit card)
# Navigate to API keys section
# Create and copy your API key
```

**Env Variable:**
```bash
CEREBRAS_API_KEY=csk_YOUR_KEY_HERE
```

---

### 5️⃣ **Cohere** (1K requests/month + $1 credits)

```bash
# Go to https://dashboard.cohere.com/api-keys
# Sign up with email
# Copy your API key
```

**Env Variable:**
```bash
COHERE_API_KEY=your_cohere_key_here
```

---

### 6️⃣ **HuggingFace** (32K tokens/month + 100K+ models)

```bash
# Go to https://huggingface.co/settings/tokens
# Sign up (no credit card)
# Create new token (read access is enough)
# Copy your API key
```

**Env Variable:**
```bash
HUGGINGFACE_API_KEY=hf_YOUR_KEY_HERE
```

---

## 🛠️ Step 2: Setup Environment

### Create `.env` file

Create `server/.env` with all your API keys:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db

# JWT Security
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_EXPIRATION_HOURS=24

# All 6 LLM Provider Keys
GROQ_API_KEY=gsk_YOUR_GROQ_KEY
GEMINI_API_KEY=AIza_YOUR_GEMINI_KEY
MISTRAL_API_KEY=your_mistral_key
CEREBRAS_API_KEY=csk_YOUR_CEREBRAS_KEY
COHERE_API_KEY=your_cohere_key
HUGGINGFACE_API_KEY=hf_YOUR_HF_KEY
```

**Important:** Never commit `.env` to Git! Add to `.gitignore`.

---

## 📦 Step 3: Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

---

## ✅ Step 4: Validate API Keys

Create a test script `test_providers.py`:

```python
import asyncio
import os
from dotenv import load_dotenv
from orchestrator_v2 import PROVIDERS, validate_all_providers, get_provider_info

load_dotenv()

async def main():
    print("\n🔍 Provider Information:")
    info = get_provider_info()
    for provider_id, details in info.items():
        status = "✅" if details["initialized"] else "❌"
        print(f"{status} {provider_id.upper()}: {details['name']}")
        print(f"   Quota: {details['quota']}")
        print()
    
    print("\n🧪 Validating API Keys...")
    results = await validate_all_providers()
    for provider_id, is_valid in results.items():
        status = "✅ Valid" if is_valid else "❌ Invalid/Missing"
        print(f"{provider_id.upper()}: {status}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python test_providers.py
```

Expected output:
```
✅ Groq: Valid
✅ Gemini: Valid
✅ Mistral: Valid
✅ Cerebras: Valid
✅ Cohere: Valid
✅ HuggingFace: Valid
```

---

## 🚀 Step 5: Start the Server

```bash
python app.py
```

You'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Visit: **http://localhost:8000/docs** for interactive API docs

---

## 📡 Step 6: Test the Orchestrator

### Using cURL

```bash
# 1. Register a user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# Response:
# {
#   "access_token": "eyJhbGc...",
#   "token_type": "bearer",
#   "user": {...}
# }

# 2. Query multiple providers
curl -X POST "http://localhost:8000/api/query" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What is the capital of France?",
    "selected_agents": ["groq", "gemini", "mistral", "cerebras", "cohere", "huggingface"]
  }'
```

### Using Python

```python
import asyncio
from orchestrator_v2 import orchestrate_query

async def test():
    result = await orchestrate_query(
        query_text="Explain quantum computing in simple terms",
        provider_ids=["groq", "gemini", "mistral", "cerebras"],
        db=None
    )
    
    print("\n=== RESPONSES ===")
    for provider_id, response in result["responses"].items():
        print(f"\n{provider_id.upper()}:")
        if response["status"] == "success":
            print(f"  Response: {response['response_text'][:200]}...")
            print(f"  Time: {response['response_time_ms']:.0f}ms")
        else:
            print(f"  Error: {response['error_message']}")
    
    print("\n=== SYNTHESIS ===")
    synthesis = result["synthesis"]
    print(f"Success Rate: {synthesis['consensus_analysis']['success_rate']*100:.0f}%")
    print(f"Common Themes: {synthesis['common_themes']}")

if __name__ == "__main__":
    asyncio.run(test())
```

---

## 🗂️ Project Structure

```
server/
├── app.py                 # FastAPI app with auth & endpoints
├── orchestrator_v2.py     # Multi-provider orchestrator
├── db.py                  # Database models
├── providers/
│   ├── __init__.py
│   ├── base_provider.py   # Abstract base class
│   ├── groq_provider.py   # Groq implementation
│   ├── gemini_provider.py # Gemini implementation
│   ├── mistral_provider.py# Mistral implementation
│   ├── cerebras_provider.py# Cerebras implementation
│   ├── cohere_provider.py # Cohere implementation
│   └── huggingface_provider.py# HuggingFace implementation
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (NOT in Git!)
└── SETUP_GUIDE.md        # This file
```

---

## 🔗 API Endpoints

### Authentication

```
POST   /api/auth/register    # Create account
POST   /api/auth/login       # Get JWT token
GET    /api/auth/me          # Get current user info
```

### Querying

```
POST   /api/query            # Query multiple providers
GET    /api/queries          # Get user's query history
GET    /api/query/{id}       # Get details of a query
```

### Admin

```
GET    /api/admin/users      # List all users (admin only)
GET    /api/admin/metrics    # System metrics (admin only)
```

### Health

```
GET    /api/health           # Health check
GET    /                      # Root endpoint with provider list
```

---

## 📊 Example Query Response

```json
{
  "query_id": 1,
  "query_text": "What is photosynthesis?",
  "responses": {
    "groq": {
      "status": "success",
      "response_text": "Photosynthesis is the process...",
      "response_time_ms": 450,
      "token_count": 156,
      "cached": false,
      "sources": []
    },
    "gemini": {
      "status": "success",
      "response_text": "Photosynthesis is a chemical reaction...",
      "response_time_ms": 820,
      "token_count": 203,
      "cached": false,
      "sources": [
        {"url": "https://example.com", "title": "Biology Basics"}
      ]
    }
  },
  "synthesis": {
    "consensus_analysis": {
      "total_providers": 2,
      "successful": 2,
      "failed": 0,
      "success_rate": 1.0
    },
    "common_themes": ["photosynthesis", "process", "light", "energy", "chlorophyll"],
    "sources_used": [...],
    "source_frequency": {...}
  },
  "metadata": {
    "total_providers": 2,
    "successful": 2,
    "avg_response_time_ms": 635,
    "cached_count": 0
  }
}
```

---

## 🐛 Troubleshooting

### "API key not found"

**Solution:** Make sure your `.env` file is in the `server/` directory and the key names match exactly (case-sensitive).

### "Request timeout"

**Solution:** Some models might be slow on first request. Increase timeout in `orchestrator_v2.py` timeout parameter or wait a moment and retry.

### "Model not found"

**Solution:** Check provider-specific model names in each `*_provider.py` file. Use `get_provider_info()` to verify.

### "No module named 'providers'"

**Solution:** Make sure you're in the `server/` directory:
```bash
cd server
python app.py
```

---

## 💰 Cost Summary

| Provider | Free Quota | Cost After | Notes |
|----------|-----------|-----------|-------|
| **Groq** | 14.4K req/day | $0 free forever | Fastest |
| **Gemini** | 15K tokens/day | $0.075/1M tokens | Web search included |
| **Mistral** | 500K tokens/month | $0.15/1M tokens | Strong reasoning |
| **Cerebras** | 1M tokens/day | $0 free forever | 20x faster than GPT-4 |
| **Cohere** | 1K req/month + $1 credits | $0.50/1M tokens | Good for text tasks |
| **HuggingFace** | 32K tokens/month + 100K+ models | Free tier is generous | Unlimited model variety |

**Total MVP Cost:** $0/month for reasonable usage

---

## 📚 Next Steps

1. ✅ Set up all 6 providers
2. ✅ Validate API keys
3. ✅ Start the server
4. ✅ Test with sample queries
5. 🔄 Build frontend (React/Next.js)
6. 📊 Add response caching & synthesis
7. 🚀 Deploy to production (Render, Railway, Vercel)

---

## 🆘 Need Help?

- **Groq Docs:** https://console.groq.com/docs
- **Gemini Docs:** https://ai.google.dev/gemini-api/docs
- **Mistral Docs:** https://docs.mistral.ai/
- **Cerebras Docs:** https://docs.cerebras.ai/
- **Cohere Docs:** https://docs.cohere.com/
- **HuggingFace Docs:** https://huggingface.co/docs/api-inference/

---

**Happy orchestrating! 🚀**
