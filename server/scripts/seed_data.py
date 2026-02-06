import os
import time
from typing import List, Dict

import pandas as pd


def _classify_domain(text: str) -> str:
	lower = text.lower()
	if any(word in lower for word in ("quantum", "physics", "gravity", "atom")):
		return "physics"
	if any(word in lower for word in ("code", "algorithm", "computer", "software")):
		return "computer_science"
	if any(word in lower for word in ("cell", "dna", "evolution", "brain")):
		return "biology"
	if any(word in lower for word in ("war", "history", "president", "ancient")):
		return "history"
	return "general"


def _estimate_complexity(text: str) -> float:
	words = text.split()
	word_score = min(len(words) / 20.0, 0.5)
	complex_words = ("why", "how", "explain", "difference", "compare")
	complex_score = 0.3 if any(w in text.lower() for w in complex_words) else 0.0
	tech_score = 0.2 if any(c.isupper() for c in text) else 0.0
	return min(word_score + complex_score + tech_score, 1.0)


def collect_eli5(limit: int = 1000) -> List[Dict[str, str]]:
	try:
		import praw
		from tqdm import tqdm
	except Exception as exc:
		raise RuntimeError("praw and tqdm are required: pip install praw tqdm") from exc

	reddit = praw.Reddit(
		client_id=os.getenv("REDDIT_CLIENT_ID", ""),
		client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
		user_agent=os.getenv("REDDIT_USER_AGENT", "worldbrain_researcher"),
	)

	queries: List[Dict[str, str]] = []
	seen_titles = set()
	for submission in tqdm(reddit.subreddit("explainlikeimfive").hot(limit=limit)):
		if submission.link_flair_text == "Explained":
			title = submission.title.replace("ELI5:", "").replace("ELI5 ", "").strip()
			if not title or len(title) < 10:
				continue
			if title in seen_titles:
				continue
			seen_titles.add(title)
			queries.append({
				"text": title,
				"domain": _classify_domain(title),
				"complexity": _estimate_complexity(title),
				"source": "eli5",
			})
			time.sleep(0.1)
	return queries


def main():
	limit = int(os.getenv("ELI5_LIMIT", "1000"))
	queries = collect_eli5(limit=limit)
	output_path = os.getenv("SEED_OUTPUT", "seed_queries.csv")

	df = pd.DataFrame(queries)
	df.to_csv(output_path, index=False)
	print(f"Collected {len(df)} seed queries -> {output_path}")


if __name__ == "__main__":
	main()
