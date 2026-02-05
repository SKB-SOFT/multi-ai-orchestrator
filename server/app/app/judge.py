import re
from typing import List, Dict, Optional

# THINKERS must be imported or defined for consensus calculation
THINKERS = [
    {"name": "groq", "model": "llama-3.3-70b-versatile", "weight": 0.40},
    {"name": "gemini", "model": "gemini-2.0-flash-exp", "weight": 0.30},
    {"name": "mistral", "model": "mistral-large-latest", "weight": 0.20},
    {"name": "ollama", "model": "llama3.1:7b", "weight": 0.10}
]

def score_response(response: Dict) -> float:
    """Score thinker response: depth + confidence + speed"""
    answer = response["answer"].lower()
    depth_keywords = "analyze compare research model vs benchmark evidence study".split()
    depth_score = sum(1 for word in depth_keywords if word in answer) / max(len(answer.split()), 1)
    fluff_keywords = "i think you like great awesome cool".split()
    fluff_penalty = sum(1 for word in fluff_keywords if word in answer) * 0.1
    return (response["confidence"] * 0.5 + 
            depth_score * 0.3 + 
            response["weight"] * 0.2 - 
            fluff_penalty)

def judge_thinkers(responses: List[Dict]) -> Dict:
    """Pick best thinker + compute consensus"""
    if not responses:
        return {"answer": "All thinkers failed. Brain resting.", 
                "confidence": 0.0, "providers_used": []}
    scored = [(score_response(r), r) for r in responses]
    scored.sort(reverse=True, key=lambda x: x[0])
    best_score, best_response = scored[0]
    providers_used = [r["thinker"] for r in responses]
    consensus = len(responses) / len(THINKERS)
    return {
        "answer": best_response["answer"],
        "confidence": min(best_score, 1.0),
        "providers_used": providers_used[:3],
        "consensus": consensus,
        "winner": best_response["thinker"]
    }
