import os
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


_EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
_EMBEDDINGS_ENABLED = os.getenv("EMBEDDINGS_ENABLED", "false").lower() == "true"
_EMBEDDING_MODEL = None


def _get_embedding_model():
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None and SentenceTransformer is not None:
        _EMBEDDING_MODEL = SentenceTransformer(_EMBEDDING_MODEL_NAME)
    return _EMBEDDING_MODEL


def compute_embedding(text: str) -> Optional[List[float]]:
    if not _EMBEDDINGS_ENABLED:
        return None
    model = _get_embedding_model()
    if model is None:
        return None
    return model.encode([text])[0].tolist()


def classify_question_type(text: str) -> str:
    first_word = re.split(r"\s+", text.strip().lower())[0] if text.strip() else ""
    known = {"what", "how", "why", "explain", "who", "when", "where", "which", "compare", "describe"}
    return first_word if first_word in known else "other"


def estimate_complexity_score(text: str) -> float:
    words = re.findall(r"\w+", text)
    word_count = len(words)
    base = min(1.0, word_count / 50.0)
    boost = 0.0
    lower = text.lower()
    if any(k in lower for k in ("compare", "contrast", "analyze", "evaluate", "tradeoff")):
        boost += 0.1
    if any(k in lower for k in ("why", "how", "explain", "derive")):
        boost += 0.1
    return max(0.0, min(1.0, base + boost))


def classify_domain(text: str) -> str:
    lower = text.lower()
    domains: Dict[str, List[str]] = {
        "Physics": ["quantum", "relativity", "particle", "gravity", "thermodynamics"],
        "Computer Science": ["algorithm", "complexity", "database", "neural", "compiler", "api"],
        "Biology": ["cell", "genome", "protein", "evolution", "enzyme"],
        "Mathematics": ["theorem", "proof", "algebra", "calculus", "probability"],
        "History": ["war", "empire", "revolution", "ancient", "century"],
        "Philosophy": ["ethics", "metaphysics", "epistemology", "ontology", "moral"],
        "General Knowledge": ["capital", "population", "country", "definition", "overview"],
    }
    for domain, keywords in domains.items():
        if any(k in lower for k in keywords):
            return domain
    return "Other"


def estimate_cost_usd(provider_id: str, token_count: Optional[int]) -> float:
    if not token_count:
        return 0.0
    pricing_per_1k = {
        "groq": 0.0,
        "gemini": 0.0,
        "mistral": 0.0,
        "cerebras": 0.0,
        "cohere": 0.0,
        "huggingface": 0.0,
    }
    per_1k = pricing_per_1k.get(provider_id, 0.0)
    return round((token_count / 1000.0) * per_1k, 6)


def get_query_metrics(text: str) -> Dict[str, Optional[float]]:
    words = re.findall(r"\w+", text)
    return {
        "query_length": len(text),
        "word_count": len(words),
        "question_type": classify_question_type(text),
        "complexity_score": estimate_complexity_score(text),
        "domain": classify_domain(text),
    }


async def log_system_metrics(db: AsyncSession) -> None:
    from server.db import Query, Response, SystemMetric  # type: ignore

    now = datetime.now(timezone.utc)
    hour_ago = now - timedelta(hours=1)

    queries_count = await db.execute(
        select(func.count(Query.query_id)).where(Query.query_timestamp >= hour_ago)
    )
    queries_count = queries_count.scalar() or 0

    total_cost = await db.execute(
        select(func.sum(Response.cost_usd))
        .select_from(Response)
        .join(Query, Response.query_id == Query.query_id)
        .where(Query.query_timestamp >= hour_ago)
    )
    total_cost = float(total_cost.scalar() or 0.0)

    total_responses = await db.execute(
        select(func.count(Response.response_id))
        .select_from(Response)
        .join(Query, Response.query_id == Query.query_id)
        .where(Query.query_timestamp >= hour_ago)
    )
    total_responses = total_responses.scalar() or 0

    error_responses = await db.execute(
        select(func.count(Response.response_id))
        .select_from(Response)
        .join(Query, Response.query_id == Query.query_id)
        .where(Query.query_timestamp >= hour_ago)
        .where(Response.status == "error")
    )
    error_responses = error_responses.scalar() or 0

    error_rate = (error_responses / total_responses * 100.0) if total_responses > 0 else 0.0

    total_queries = await db.execute(
        select(func.count(Query.query_id)).where(Query.query_timestamp >= hour_ago)
    )
    total_queries = total_queries.scalar() or 0

    rejected = await db.execute(
        select(func.count(Query.query_id))
        .where(Query.query_timestamp >= hour_ago)
        .where(Query.accepted == False)
    )
    rejected = rejected.scalar() or 0
    rejection_rate = (rejected / total_queries * 100.0) if total_queries > 0 else 0.0

    db.add(SystemMetric(
        queries_processed_hour=queries_count,
        total_cost_usd=total_cost,
        uptime_percent=100.0,
        error_rate_percent=error_rate,
        gatekeeper_rejection_rate=rejection_rate,
    ))
    await db.commit()
