import os
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine


def _normalize_db_url(raw_url: str) -> str:
    if raw_url.startswith("postgresql+asyncpg"):
        return raw_url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)
    return raw_url


def _get_engine():
    raw_url = os.getenv("DATABASE_URL", "sqlite:///../data/app.db")
    url = _normalize_db_url(raw_url)
    return create_engine(url)


def main():
    engine = _get_engine()

    totals = pd.read_sql(
        """
        SELECT COUNT(*) as total_queries
        FROM queries
        """,
        engine,
    )

    human_evals = pd.read_sql(
        """
        SELECT COUNT(*) as total_human_evals
        FROM human_evaluations
        """,
        engine,
    )

    date_range = pd.read_sql(
        """
        SELECT MIN(query_timestamp) as first_ts, MAX(query_timestamp) as last_ts
        FROM queries
        WHERE accepted = 1
        """,
        engine,
    )

    win_rates = pd.read_sql(
        """
        SELECT winning_model, COUNT(*) as wins
        FROM judge_decisions
        GROUP BY winning_model
        ORDER BY wins DESC
        """,
        engine,
    )

    avg_latency = pd.read_sql(
        """
        SELECT AVG(response_time_ms) as avg_response_time_ms
        FROM responses
        WHERE response_time_ms IS NOT NULL
        """,
        engine,
    )

    total_cost = pd.read_sql(
        """
        SELECT SUM(cost_usd) as total_cost_usd
        FROM responses
        WHERE cost_usd IS NOT NULL
        """,
        engine,
    )

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    first_ts = date_range["first_ts"][0]
    last_ts = date_range["last_ts"][0]
    date_span = "N/A"
    if first_ts and last_ts:
        date_span = f"{first_ts} to {last_ts}"

    total_queries = int(totals["total_queries"][0]) if not totals.empty else 0
    total_human_evals = int(human_evals["total_human_evals"][0]) if not human_evals.empty else 0
    total_cost_usd = float(total_cost["total_cost_usd"][0] or 0) if not total_cost.empty else 0.0
    avg_latency_ms = round(float(avg_latency["avg_response_time_ms"][0] or 0), 2) if not avg_latency.empty else 0.0

    report_lines = [
        "# World Brain Research Report",
        "",
        f"Generated: {now}",
        "",
        "## Summary",
        f"- Total queries: {total_queries}",
        f"- Human evaluations: {total_human_evals}",
        f"- Date range: {date_span}",
        f"- Average response time (ms): {avg_latency_ms}",
        f"- Total cost (USD): {round(total_cost_usd, 2)}",
        "",
        "## Win Rates",
    ]

    if not win_rates.empty:
        report_lines.append("| Model | Wins |")
        report_lines.append("| --- | --- |")
        for _, row in win_rates.iterrows():
            report_lines.append(f"| {row['winning_model']} | {int(row['wins'])} |")
    else:
        report_lines.append("No judge decisions recorded yet.")

    output_path = os.getenv("REPORT_OUTPUT", "../docs/report-generated.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
