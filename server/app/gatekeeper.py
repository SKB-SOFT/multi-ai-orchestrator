import os
from typing import List

class Gatekeeper:
    def is_research_query(self, query: str) -> bool:
        """
        Determines if a query is complex enough for research.
        - Word count > 5
        - Ends with "?" OR contains a question word.
        """
        words = query.split()
        if len(words) <= 5:
            return False

        query_lower = query.lower()
        question_words = ["explain", "compare", "why", "how", "what"]
        
        if query.strip().endswith("?") or any(word in query_lower for word in question_words):
            return True
            
        return False
gatekeeper = Gatekeeper()
