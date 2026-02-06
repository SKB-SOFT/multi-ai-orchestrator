# Reporting, Dashboard, and Evaluation

This guide covers the current reporting workflow, dashboard, human evaluation UI, and ablation runs.

## Implementation Summary (What Was Implemented)

The system now captures research-grade data end-to-end. The database schema was expanded to include
query metadata (length, domain, complexity, acceptance), rich response fields (latency, tokens, cost,
cache status), and dedicated tables for judge decisions, memory retrievals, human evaluations, and
system metrics. Optional pgvector support is wired in for embeddings when using PostgreSQL.

The query pipeline logs metrics for every request, including derived question characteristics and
cost estimates, and records a minimal judge decision based on the synthesis provider. A background
metrics loop runs inside the API process to roll up hourly system stats such as throughput, error
rate, and rejection rate.

For analysis and reporting, the project includes a Markdown report generator and a cross-platform
PDF export pipeline. A live Streamlit dashboard shows real-time stats (volume, win rates, quality
trend, domains, recent queries, and cost over time). There is also a Streamlit human evaluation UI to
collect rater scores directly into the database, plus a seed data script for ELI5 collection and an
ablation runner to reprocess sampled queries with different provider sets.

Finally, optional analysis dependencies and environment variables are documented to support embeddings,
dashboarding, and reporting without changing the core API setup.

## Generate a Markdown Report

From the repo root:

```bash
python server/scripts/generate_report.py
```

This writes docs/report-generated.md with totals, date range, latency, and cost summary.

## Export to PDF

Install Pandoc, then run:

```powershell
./scripts/build_report.ps1
```

or on Linux/macOS:

```bash
./scripts/build_report.sh
```

The PDF export expects docs/report-generated.md to exist. Generate it first.

## Dashboard

Run the Streamlit dashboard:

```bash
streamlit run server/scripts/dashboard_app.py
```

It includes total queries, queries today, average cost, human eval count, win rates, quality trend,
domain distribution, recent queries, and cost over time.

## Human Evaluation UI

Collect human ratings with the Streamlit UI:

```bash
streamlit run server/scripts/human_eval_ui.py
```

Set EVALUATOR_ID in the environment to tag evaluations.

## Ablation Runner

Re-run sampled queries with different provider sets:

```bash
python server/scripts/run_ablation.py
```

## Seed Data Loader

Pull ELI5 seed queries:

```bash
python server/scripts/seed_data.py
```

Set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT before running.

## System Metrics Loop

System metrics are logged automatically by the API process. Tune the interval with:

```
METRICS_INTERVAL_SECONDS=3600
```

## Optional Dependencies

Install analysis and dashboard dependencies:

```bash
pip install -r server/requirements-analysis.txt
```

## Troubleshooting

### Dashboard shows "No data"
- Ensure at least one query has been processed through the API.
- Check database connectivity.
- Verify accepted queries exist: SELECT COUNT(*) FROM queries WHERE accepted=true;

### PDF export fails
- Verify Pandoc is installed: pandoc --version
- Ensure docs/report-generated.md exists.
- On Windows, try running PowerShell as Administrator if permissions fail.

### Human eval UI shows no queries
- Run seed data: python server/scripts/seed_data.py
- Or process organic queries through the API.
- Check unevaluated count: SELECT COUNT(*) FROM queries WHERE query_id NOT IN (SELECT query_id FROM human_evaluations);

### Embeddings not generating
- Set EMBEDDINGS_ENABLED=true in server/.env
- Install sentence-transformers: pip install sentence-transformers
- For PostgreSQL, ensure pgvector is enabled: CREATE EXTENSION vector;

### System metrics table is empty
- The background loop runs inside the API process.
- Start the API and wait for the interval (default 3600s).
- Set METRICS_INTERVAL_SECONDS to a smaller value for testing.

## Quick Start (Research Pipeline)

### Day 1: Setup
```bash
pip install -r server/requirements.txt
pip install -r server/requirements-analysis.txt

copy server/.env.example server/.env
```

Edit server/.env with DATABASE_URL, API keys, and EMBEDDINGS_ENABLED=true.

Initialize the database by starting the API:

```bash
uvicorn server.app:app
```

### Week 1: Baseline Collection
```bash
python server/scripts/seed_data.py
```

Process queries via the API. Then collect human evals:

```bash
streamlit run server/scripts/human_eval_ui.py
```

Generate the baseline report:

```bash
python server/scripts/generate_report.py
./scripts/build_report.sh
```

### Weeks 2-8: Learning Phase
- Process 1,000 queries per week.
- Generate a report snapshot every 1,000 queries.
- Continue human evaluations (about 50 per batch).

### Week 9: Validation and Ablation
```bash
python server/scripts/run_ablation.py
python server/scripts/generate_report.py
./scripts/build_report.sh
```

## Data Quality Checklist (Before Writing Paper)

Minimum thresholds (Tier 2):

- 5,000+ accepted queries: SELECT COUNT(*) FROM queries WHERE accepted=true;
- 500+ human evaluations: SELECT COUNT(*) FROM human_evaluations;
- 10% eval coverage: 500/5000 = 10%
- 5+ domains: SELECT COUNT(DISTINCT domain) FROM queries WHERE accepted=true;
- 30+ days of data: SELECT (MAX(query_timestamp) - MIN(query_timestamp)) FROM queries;

Quality signals:

- Gatekeeper working: 15-25% rejected (accepted=false)
- Judge decisions logged for accepted queries
- Win rates are diverse (no model > 60%)
- Cost data present for most responses

## Performance Optimization

For large datasets (>10K queries):

- Add indexes for dashboard queries and batching.
- Cache dashboard queries with streamlit cache if needed.
- For embeddings, add an ivfflat index in pgvector when on PostgreSQL.

## Research Methodology Pointer

This implementation follows the plan in docs/research-plan-v1.md for query targets,
experimental protocol, and statistical requirements.
