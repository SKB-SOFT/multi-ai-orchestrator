import os
from typing import List

class Gatekeeper:
    def __init__(self):
        self.reject_patterns = os.getenv("REJECT_PATTERNS", "pizza|weather|jokes|dress|favorite|recipe|outfit|football|music|restaurant").split("|")
        self.pass_patterns = os.getenv("PASS_PATTERNS", "analyze|compare|research|model|vs|explain|how|why|architecture|algorithm").split("|")
    def is_research_query(self, query: str) -> bool:
        query_lower = query.lower()
        return (not any(p in query_lower for p in self.reject_patterns) and any(p in query_lower for p in self.pass_patterns))
gatekeeper = Gatekeeper()
