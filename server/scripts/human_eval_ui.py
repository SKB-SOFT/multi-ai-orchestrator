import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine


def _normalize_db_url(raw_url: str) -> str:
    if raw_url.startswith("postgresql+asyncpg"):
        return raw_url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)
    return raw_url


def _get_engine():
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        # Check common locations for app.db
        candidates = ["app.db", "server/data/app.db", "data/app.db", "../data/app.db"]
        db_path = "app.db"
        for c in candidates:
            if os.path.exists(c):
                db_path = c
                break
        raw_url = f"sqlite:///{db_path}"
    
    url = _normalize_db_url(raw_url)
    return create_engine(url)


def main():
    st.set_page_config(page_title="Human Evaluation", layout="wide")
    st.title("Human Evaluation Interface")

    engine = _get_engine()

    unevaluated = pd.read_sql(
        """
        SELECT q.query_id,
               q.query_text,
               jd.winning_response_id,
               r.response_text
        FROM queries q
        JOIN judge_decisions jd ON q.query_id = jd.query_id
        JOIN responses r ON jd.winning_response_id = r.response_id
        WHERE q.query_id NOT IN (SELECT query_id FROM human_evaluations)
        ORDER BY RANDOM()
        LIMIT 1
        """,
        engine,
    )

    if unevaluated.empty:
        st.success("All queries evaluated.")
        return

    row = unevaluated.iloc[0]

    st.subheader("Question")
    st.write(row["query_text"])

    st.subheader("AI Answer")
    st.write(row["response_text"])

    st.subheader("Your Evaluation")
    correctness = st.slider("Correctness (1 = wrong, 5 = perfect)", 1, 5, 3)
    helpfulness = st.slider("Helpfulness (1 = useless, 5 = excellent)", 1, 5, 3)
    overall = st.slider("Overall Quality (1 = poor, 5 = excellent)", 1, 5, 3)
    trust = st.radio("Would you trust this answer?", ["Yes", "No"])
    comments = st.text_area("Optional comments")

    if st.button("Submit Evaluation"):
        payload = pd.DataFrame([
            {
                "query_id": int(row["query_id"]),
                "response_id": int(row["winning_response_id"]),
                "evaluator_id": os.getenv("EVALUATOR_ID", "anonymous"),
                "quality_score": int(overall),
                "correctness": True if correctness >= 4 else False,
                "helpfulness_score": int(helpfulness),
                "comments": comments,
            }
        ])
        payload.to_sql("human_evaluations", engine, if_exists="append", index=False)
        st.success("Evaluation saved.")
        st.experimental_rerun()


if __name__ == "__main__":
    main()
