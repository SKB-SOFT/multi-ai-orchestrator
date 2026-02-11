from typing import List, Dict
import re

def score_response(response: Dict, query: str) -> float:
    """
    Scores a response based on length, specificity, and directness.
    """
    answer = response.get("answer", "")
    if not answer:
        return 0.0

    # 1. Length score (favoring substantial answers)
    length = len(answer.split())
    length_score = min(length / 150, 1.0) # Normalize to 0-1, capping at 150 words

    # 2. Specificity score (presence of numbers, keywords from query)
    numbers = re.findall(r'\d+', answer)
    specificity_score = len(numbers) * 0.1

    query_words = set(query.lower().split())
    answer_words = set(answer.lower().split())
    shared_words = query_words.intersection(answer_words)
    specificity_score += len(shared_words) / max(len(query_words), 1) * 0.5

    # 3. Directness (penalize filler words)
    filler_words = ["i think", "in my opinion", "personally", "i feel", "it seems"]
    filler_penalty = sum(1 for phrase in filler_words if phrase in answer.lower()) * 0.2

    # Combine scores
    total_score = (length_score * 0.4) + (specificity_score * 0.6) - filler_penalty
    
    # Add original confidence and weight
    total_score += response.get("confidence", 0.0) * 0.1
    total_score += response.get("weight", 0.0) * 0.1

    return max(0, total_score) # Ensure score is not negative

def judge_thinkers(responses: List[Dict], query: str) -> Dict:
    if not responses:
        return {
            "answer": "All thinkers are currently offline. Please try again later.",
            "confidence": 0.0,
            "providers_used": [],
        }

    scored_responses = [(score_response(r, query), r) for r in responses]
    scored_responses.sort(reverse=True, key=lambda x: x[0])

    # For now, we'll still pick the single best one.
    # The next step is to synthesize the top 2-3.
    best_score, best_response = scored_responses[0]
    
    providers_used = [r["thinker"] for r in responses]

    return {
        "answer": best_response["answer"],
        "confidence": min(best_score, 1.0),
        "providers_used": providers_used,
        "winner": best_response["thinker"],
        "all_scores": {r["thinker"]: score for score, r in scored_responses}
    }
