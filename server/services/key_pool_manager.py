import os
from typing import List, Dict, Optional
from collections import defaultdict
import time

class KeyPoolManager:
    """
    Manages multiple API keys per provider with rotation and rate limiting.
    Distributes requests across keys to avoid hitting individual key limits.
    """
    
    def __init__(self):
        self.key_pools = self._initialize_key_pools()
        self.key_usage = defaultdict(lambda: defaultdict(int))  # provider -> key_index -> count
        self.key_last_reset = defaultdict(lambda: defaultdict(float))  # provider -> key_index -> timestamp
        self.rotation_index = defaultdict(int)  # provider -> current_index
        self.bad_keys = defaultdict(set)  # provider -> set of bad key indices
        
    def _initialize_key_pools(self) -> Dict[str, List[str]]:
        """Initialize key pools from environment variables (3 keys per provider)"""
        pools = {}
        
        providers = ["GROQ", "GEMINI", "MISTRAL", "COHERE", "CEREBRAS", "HUGGINGFACE"]
        
        for provider in providers:
            keys = []
            for i in range(1, 4):  # Keys 1, 2, 3
                key = os.getenv(f"{provider}_API_KEY_{i}")
                if key and key != f"{provider.lower()}_YOUR_KEY_{i}_HERE":
                    keys.append(key)
            
            if keys:
                pools[provider.lower()] = keys
                print(f"✓ {provider}: {len(keys)} key(s) loaded")
            else:
                print(f"⚠ {provider}: No valid keys found")
        
        return pools
    
    def get_key(self, provider: str) -> Optional[str]:
        """
        Get next available API key for provider with round-robin rotation.
        Skips keys marked as bad.
        """
        provider = provider.lower()
        
        if provider not in self.key_pools:
            raise ValueError(f"Provider '{provider}' not configured")
        
        keys = self.key_pools[provider]
        if not keys:
            raise ValueError(f"No API keys available for '{provider}'")
        
        # Try to find a non-bad key
        attempts = 0
        total_keys = len(keys)
        
        while attempts < total_keys:
            idx = self.rotation_index[provider]
            # Advance rotation for next time
            self.rotation_index[provider] = (idx + 1) % total_keys
            attempts += 1
            
            if idx not in self.bad_keys[provider]:
                key = keys[idx]
                self.key_usage[provider][idx] += 1
                return key
        
        # All keys are marked bad, but we still return one as fallback (or could raise error)
        # Use first one as ultimate fallback
        return keys[0]
    
    def mark_key_bad(self, provider: str, key: str):
        """Mark a specific key as bad so it's skipped in rotation"""
        provider = provider.lower()
        if provider in self.key_pools:
            try:
                idx = self.key_pools[provider].index(key)
                self.bad_keys[provider].add(idx)
                print(f"⚠ Key {idx+1} for {provider} marked as BAD and will be skipped")
            except ValueError:
                pass
    
    def get_primary_key(self, provider: str) -> Optional[str]:
        """Get the first/primary key without rotation"""
        provider = provider.lower()
        
        if provider not in self.key_pools or not self.key_pools[provider]:
            raise ValueError(f"No API keys available for '{provider}'")
        
        return self.key_pools[provider][0]
    
    def get_all_keys(self, provider: str) -> List[str]:
        """Get all available keys for a provider (for failover)"""
        provider = provider.lower()
        
        if provider not in self.key_pools:
            return []
        
        return self.key_pools[provider]
    
    def get_key_stats(self) -> Dict:
        """Get usage statistics for all keys"""
        stats = {}
        
        for provider, keys in self.key_pools.items():
            stats[provider] = {
                "total_keys": len(keys),
                "current_index": self.rotation_index[provider],
                "usage_per_key": dict(self.key_usage[provider])
            }
        
        return stats
    
    def reset_stats(self):
        """Reset usage statistics (useful for daily resets)"""
        self.key_usage = defaultdict(lambda: defaultdict(int))
        self.rotation_index = defaultdict(int)
        print("✓ Key usage statistics reset")
    
    def is_key_available(self, provider: str) -> bool:
        """Check if provider has available keys"""
        return provider.lower() in self.key_pools and bool(self.key_pools[provider.lower()])
    
    def get_key_count(self, provider: str) -> int:
        """Get number of available keys for a provider"""
        provider = provider.lower()
        return len(self.key_pools.get(provider, []))


# Global instance
_key_pool_manager = None

def get_key_pool_manager() -> KeyPoolManager:
    """Get or create the global KeyPoolManager instance"""
    global _key_pool_manager
    if _key_pool_manager is None:
        _key_pool_manager = KeyPoolManager()
    return _key_pool_manager
