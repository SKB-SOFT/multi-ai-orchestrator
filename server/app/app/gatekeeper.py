import os
from typing import List

class Gatekeeper:
    def __init__(self):
        self.reject_patterns = os.getenv("REJECT_PATTERNS", "pizza|weather|jokes|dress|favorite|recipe|outfit").split("|")
        self.pass_patterns = os.getenv("PASS_PATTERNS", "analyze|compare|research|model|vs|explain|how|why|architecture").split("|")
    
    def is_research_query(self, query: str) -> bool:
        query_lower = query.lower()
        if any(pattern in query_lower for pattern in self.reject_patterns):
            return False
        if not any(pattern in query_lower for pattern in self.pass_patterns):
            return False
        return True

gatekeeper = Gatekeeper()
