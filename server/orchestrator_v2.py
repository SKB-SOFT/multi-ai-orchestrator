import hashlib
import time
import asyncio
from typing import List, Dict, Any
from providers import (
    GroqProvider,
    GeminiProvider,
    MistralProvider,
    CerebrasProvider,
    CohereProvider,
    HuggingFaceProvider,
)
import os
from dotenv import load_dotenv

load_dotenv()

# ==================== PROVIDER REGISTRY ====================

PROVIDER_CONFIGS = {
    "groq": {
        "class": GroqProvider,
        "api_key_env": "GROQ_API_KEY",
        "default_model": "llama-3.3-70b-versatile",
        "name": "Groq",
        "tier": "free",
        "quota": "14.4K req/day",
    },
    "gemini": {
        "class": GeminiProvider,
        "api_key_env": "GEMINI_API_KEY",
        "default_model": "gemini-pro",
        "name": "Google Gemini",
        "tier": "free",
        "quota": "60 req/min, 15K tokens/day",
    },
    "mistral": {
        "class": MistralProvider,
        "api_key_env": "MISTRAL_API_KEY",
        "default_model": "mistral-large-latest",
        "name": "Mistral AI",
        "tier": "free",
        "quota": "1 req/sec, 500K tokens/month",
    },
    "cerebras": {
        "class": CerebrasProvider,
        "api_key_env": "CEREBRAS_API_KEY",
        "default_model": "llama-3.1-70b",
        "name": "Cerebras",
        "tier": "free",
        "quota": "1M tokens/day (!)",
    },
    "cohere": {
        "class": CohereProvider,
        "api_key_env": "COHERE_API_KEY",
        "default_model": "command-r-plus",
        "name": "Cohere",
        "tier": "free",
        "quota": "1K requests/month + $1 credits",
    },
    "huggingface": {
        "class": HuggingFaceProvider,
        "api_key_env": "HUGGINGFACE_API_KEY",
        "default_model": "HuggingFaceH4/zephyr-7b-beta",
        "name": "HuggingFace",
        "tier": "free",
        "quota": "32K tokens/month + 100K+ models",
    },
}

# Initialize providers from environment
PROVIDERS = {}
for provider_id, config in PROVIDER_CONFIGS.items():
    api_key = os.getenv(config["api_key_env"])
    if api_key:
        try:
            # HuggingFace uses model_id instead of model_name
            if provider_id == "huggingface":
                PROVIDERS[provider_id] = config["class"](
                    api_key=api_key,
                    model_id=config["default_model"]
                )
            else:
                PROVIDERS[provider_id] = config["class"](
                    api_key=api_key,
                    model_name=config["default_model"]
                )
        except Exception as e:
            print(f"Warning: Failed to initialize {provider_id}: {e}")

# ==================== UTILITY FUNCTIONS ====================

def generate_query_hash(query_text: str, agent_ids: List[str]) -> str:
    """
    Generate SHA-256 hash of query + agents for caching.
    """
    content = f"{query_text}:{'|'.join(sorted(agent_ids))}"
    return hashlib.sha256(content.encode()).hexdigest()

class ResponseSynthesizer:
    """
    Synthesize responses from multiple providers.
    """
    
    @staticmethod
    def aggregate_responses(responses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate responses from multiple providers.
        """
        successful_responses = {k: v for k, v in responses.items() if v["status"] == "success"}
        failed_responses = {k: v for k, v in responses.items() if v["status"] == "error"}
        
        # Consensus analysis
        consensus_analysis = {
            "total_providers": len(responses),
            "successful": len(successful_responses),
            "failed": len(failed_responses),
            "success_rate": len(successful_responses) / len(responses) if responses else 0,
        }
        
        # Collect all sources
        all_sources = []
        source_counts = {}
        for response in successful_responses.values():
            for source in response.get("sources", []):
                source_key = source.get("url") or source.get("type", "unknown")
                source_counts[source_key] = source_counts.get(source_key, 0) + 1
                if source not in all_sources:
                    all_sources.append(source)
        
        # Find consensus topics (common words in responses)
        response_texts = [r.get("response_text", "") for r in successful_responses.values()]
        consensus_topics = ResponseSynthesizer._extract_common_topics(response_texts)
        
        return {
            "consensus_analysis": consensus_analysis,
            "common_themes": consensus_topics,
            "sources_used": all_sources,
            "source_frequency": source_counts,
            "responses_by_provider": responses,
        }
    
    @staticmethod
    def _extract_common_topics(texts: List[str], top_n: int = 5) -> List[str]:
        """
        Extract common topics from multiple texts.
        Simple word frequency analysis.
        """
        if not texts:
            return []
        
        # Common stopwords to exclude
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "are", "was", "were", "be", "been", "being"}
        
        word_freq = {}
        for text in texts:
            words = [w.lower() for w in text.split() if w.lower() not in stopwords and len(w) > 3]
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and get top N
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [word for word, _ in top_words]

# ==================== MAIN ORCHESTRATION ====================

async def orchestrate_query(
    query_text: str,
    provider_ids: List[str],
    db=None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Orchestrate parallel queries to multiple AI providers.
    
    Args:
        query_text: User's prompt
        provider_ids: List of provider IDs to query (e.g., ["groq", "gemini", "mistral"])
        db: Database session (optional, for caching)
        timeout: Timeout per request in seconds
    
    Returns:
        {
            "responses": {provider_id: response_data},
            "synthesis": synthesis_data,
            "metadata": {
                "total_providers": int,
                "successful": int,
                "avg_response_time_ms": float,
                "cached_count": int,
            }
        }
    """
    
    query_hash = generate_query_hash(query_text, provider_ids)
    cached_responses = {}
    uncached_providers = []
    
    # Check cache if DB available
    if db:
        from sqlalchemy import select
        from db import Cache
        
        for provider_id in provider_ids:
            try:
                result = await db.execute(
                    select(Cache).where(
                        (Cache.query_hash == query_hash) & (Cache.agent_id == provider_id)
                    )
                )
                cached = result.scalar_one_or_none()
                
                if cached:
                    cached_responses[provider_id] = {
                        "status": "success",
                        "response_text": cached.response_text,
                        "response_time_ms": 0,
                        "cached": True,
                    }
                else:
                    uncached_providers.append(provider_id)
            except Exception:
                uncached_providers.append(provider_id)
    else:
        uncached_providers = provider_ids
    
    # Query uncached providers in parallel
    tasks = []
    valid_providers = []
    
    for provider_id in uncached_providers:
        if provider_id not in PROVIDERS:
            print(f"Warning: Provider '{provider_id}' not found or not initialized")
            continue
        
        valid_providers.append(provider_id)
        tasks.append(PROVIDERS[provider_id].query(query_text, timeout=timeout))
    
    # Execute all queries in parallel
    new_responses = {}
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for provider_id, result in zip(valid_providers, results):
            if isinstance(result, Exception):
                new_responses[provider_id] = {
                    "status": "error",
                    "error_message": str(result),
                    "cached": False,
                }
            else:
                new_responses[provider_id] = {
                    **result,
                    "cached": False,
                }
                
                # Cache successful responses
                if db and result["status"] == "success":
                    try:
                        from db import Cache
                        cache_entry = Cache(
                            query_hash=query_hash,
                            agent_id=provider_id,
                            response_text=result["response_text"],
                        )
                        db.add(cache_entry)
                    except Exception as e:
                        print(f"Warning: Failed to cache {provider_id}: {e}")
    
    # Commit cache to DB
    if db:
        try:
            await db.commit()
        except Exception as e:
            print(f"Warning: Failed to commit cache: {e}")
    
    # Combine all responses
    all_responses = {**cached_responses, **new_responses}
    
    # Synthesize
    synthesis = ResponseSynthesizer.aggregate_responses(all_responses)
    
    # Calculate metadata
    successful = [r for r in all_responses.values() if r["status"] == "success"]
    response_times = [r.get("response_time_ms", 0) for r in successful if not r.get("cached", False)]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    return {
        "responses": all_responses,
        "synthesis": synthesis,
        "metadata": {
            "total_providers": len(provider_ids),
            "successful": len(successful),
            "failed": len(all_responses) - len(successful),
            "avg_response_time_ms": avg_response_time,
            "cached_count": len(cached_responses),
            "query_hash": query_hash,
        }
    }

# ==================== HELPER FUNCTIONS ====================

async def validate_all_providers() -> Dict[str, bool]:
    """
    Validate all initialized providers.
    Returns status of each provider.
    """
    results = {}
    tasks = [(pid, provider.validate_key()) for pid, provider in PROVIDERS.items()]
    
    for provider_id, task in tasks:
        try:
            results[provider_id] = await task
        except Exception as e:
            print(f"Error validating {provider_id}: {e}")
            results[provider_id] = False
    
    return results

def get_provider_info() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all available providers.
    """
    info = {}
    for provider_id, config in PROVIDER_CONFIGS.items():
        is_initialized = provider_id in PROVIDERS
        info[provider_id] = {
            "name": config["name"],
            "tier": config["tier"],
            "quota": config["quota"],
            "initialized": is_initialized,
            "default_model": config["default_model"],
        }
    return info
