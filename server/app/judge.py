from typing import List, Dict

def score_response(response: Dict) -> float:
    answer = response["answer"].lower()
    depth_keywords = "analyze compare research model benchmark evidence study".split()
    depth_score = sum(1 for word in depth_keywords if word in answer) / max(len(answer.split()), 1)
    fluff_keywords = "i think you like great awesome cool".split()
    fluff_penalty = sum(1 for word in fluff_keywords if word in answer) * 0.1
    return (response["confidence"] * 0.5 + depth_score * 0.3 + response["weight"] * 0.2 - fluff_penalty)

def judge_thinkers(responses: List[Dict]) -> Dict:
    if not responses:
        return {
            "answer": "All thinkers offline. Try again later.",
            "confidence": 0.0,
            "providers_used": [],
            "consensus": 0.0
        }
    scored = [(score_response(r), r) for r in responses]
    scored.sort(reverse=True, key=lambda x: x[0])
    best_score, best_response = scored[0]
    providers_used = [r["thinker"] for r in responses]
    return {
        "answer": best_response["answer"],
        "confidence": min(best_score, 1.0),
        "providers_used": providers_used[:3],
        "consensus": len(responses) / 4.0,
        "winner": best_response["thinker"]
    }
