from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time

class BaseProvider(ABC):
    """
    Abstract base class for all LLM providers.
    Defines the interface that all providers must implement.
    Supports multiple API keys with automatic rotation.
    """
    
    def __init__(self, api_key: str, model_name: str, api_keys: Optional[List[str]] = None):
        """
        Initialize provider with single or multiple API keys.
        
        Args:
            api_key: Primary API key (for backward compatibility)
            model_name: Model name to use
            api_keys: List of API keys for rotation (optional)
        """
        self.api_key = api_key
        self.api_keys = api_keys or [api_key]  # Use single key if no list provided
        self.current_key_index = 0
        self.model_name = model_name
        self.provider_name = self.__class__.__name__
    
    def get_next_key(self) -> str:
        """Get next API key with round-robin rotation"""
        key = self.api_keys[self.current_key_index]
        self._last_key_used = key
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    def get_last_key_used(self) -> str:
        """Get the key that was most recently returned by get_next_key"""
        return getattr(self, "_last_key_used", self.api_keys[0])
    
    def get_current_key(self) -> str:
        """Get current API key without rotation"""
        return self.api_keys[self.current_key_index]
    
    def update_api_keys(self, keys: List[str]):
        """Update the list of available API keys"""
        if keys:
            self.api_keys = keys
            self.current_key_index = 0
    
    @abstractmethod
    async def query(self, prompt: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Query the provider with a prompt.
        
        Returns:
            {
                "status": "success" | "error",
                "response_text": str,
                "response_time_ms": float,
                "token_count": int,
                "error_message": str (if error),
                "sources": list (if available),
                "model_used": str,
                "provider": str
            }
        """
        pass
    
    @abstractmethod
    async def validate_key(self) -> bool:
        """
        Validate that the API key is valid.
        """
        pass
    
    def format_response(self, response_text: str, response_time_ms: float, 
                       token_count: int = None, sources: list = None) -> Dict[str, Any]:
        """
        Format a successful response in the standard format.
        """
        if token_count is None:
            token_count = len(response_text.split())
        
        return {
            "status": "success",
            "response_text": response_text[:5000],  # Truncate for DB
            "response_time_ms": response_time_ms,
            "token_count": token_count,
            "sources": sources or [],
            "model_used": self.model_name,
            "provider": self.provider_name,
        }
    
    def format_error(
        self,
        error_message: str,
        response_time_ms: float,
        error_type: str = "unknown",
        retry_after_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Format an error response in the standard format.
        """
        return {
            "status": "error",
            "error_type": error_type,
            "error_message": error_message[:500],
            "retry_after_ms": retry_after_ms,
            "response_time_ms": response_time_ms,
            "model_used": self.model_name,
            "provider": self.provider_name,
        }
