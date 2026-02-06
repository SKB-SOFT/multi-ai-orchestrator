import asyncio
import os
from typing import Dict, List

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from server.db import Query
from server.orchestrator_v2 import orchestrate_query


def _normalize_db_url(raw_url: str) -> str:
    if raw_url.startswith("postgresql+asyncpg"):
        return raw_url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)
    return raw_url


def _get_engine():
    raw_url = os.getenv("DATABASE_URL", "sqlite:///../data/app.db")
    url = _normalize_db_url(raw_url)
    return create_engine(url)


def _get_sample_query_ids(db: Session, limit: int = 500) -> List[int]:
    rows = (
        db.query(Query.query_id)
        .filter(Query.query_id >= 2000)
        .filter(Query.query_id <= 7000)
        .filter(Query.accepted == True)
        .order_by(func.random())
        .limit(limit)
        .all()
    )
    return [row[0] for row in rows]


async def _run_ablation(db: Session, query_ids: List[int], provider_ids: List[str], label: str) -> None:
    for qid in query_ids:
        query = db.query(Query).filter(Query.query_id == qid).first()
        if not query:
            continue
        await orchestrate_query(
            user_id=query.user_id,
            query_text=query.query_text,
            provider_ids=provider_ids,
            db=None,
        )
    print(f"Completed ablation: {label} ({len(query_ids)} queries)")


def main():
    engine = _get_engine()
    db = Session(engine)

    query_ids = _get_sample_query_ids(db)

    configs: Dict[str, List[str]] = {
        "baseline": ["groq", "gemini", "mistral", "cerebras", "cohere", "huggingface"],
        "single_model_groq": ["groq"],
        "single_model_gemini": ["gemini"],
    }

    for label, providers in configs.items():
        asyncio.run(_run_ablation(db, query_ids, providers, label))

    db.close()


if __name__ == "__main__":
    main()
