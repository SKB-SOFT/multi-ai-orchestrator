# V1 Data Collection Plan for Research Paper

## Executive Summary

To transform your World Brain project into a publishable arXiv paper, you need to systematically collect quantitative metrics, qualitative patterns, and experimental evidence across approximately 5,000-10,000 queries. This document outlines exactly what data to track, how to structure your experiments, and when you will have enough evidence for a strong paper.

Bottom line: with proper instrumentation from day one, 5,000 well-distributed queries should give you sufficient data for an arXiv preprint. 10,000 queries will make it conference-ready.

---

## Part 1: What to Collect (7 Categories)

### Category 1: Query Characteristics

Track every incoming query with these attributes:

- Basic metrics: query text, timestamp, character count, word count, question type (what/how/why/explain)
- Complexity score: your gatekeeper's 0-1 score determining if query is worthy
- Domain classification: use a simple classifier (or GPT-4 with structured output) to tag queries as Physics, Computer Science, Biology, Mathematics, History, Philosophy, General Knowledge, or Other
- Accept/reject decision: did the gatekeeper let it through? If rejected, log the reason (too simple, off-topic, profanity, malformed)
- Embedding vector: store sentence-transformer embeddings for every query (you will need this for similarity analysis later)
- User context: anonymized user ID (hash), session ID, geographic region (optional)

Why this matters: you will analyze whether your system improves differently across domains, complexity levels, and query types. Papers love graphs showing performance on simple vs complex queries over time.

---

### Category 2: Model Performance Data

For every accepted query, collect responses from all 4 models:

- Individual responses: full text from Groq, Gemini, Mistral, OpenAI
- Response time: latency in milliseconds for each model
- Token counts: input tokens, output tokens (for cost analysis)
- Cost per response: calculate actual cost using provider pricing (Groq is often free, OpenAI costs $X per 1K tokens)
- Model-provided confidence: if the API returns confidence scores, log them
- Error tracking: did any model fail? Timeout? Return gibberish?

Why this matters: you will create comparison tables showing model X wins 35% on physics queries but only 12% on biology, and cost-efficiency graphs showing our ensemble costs 6.2x less than GPT-4 alone while matching quality.

---

### Category 3: Judge Decisions

Your judge (likely GPT-4 or Claude) picks the best answer. Log:

- Winning model: which of the 4 responses was chosen
- Scoring breakdown: accuracy score (0-10), coherence score (0-10), completeness score (0-10)
- Judge reasoning: the text explanation of why this answer won
- Unanimous vs split: did all criteria agree, or was it close (e.g., Model A best accuracy but Model B best coherence)
- Tie-breaking events: when two models scored identically, how did you break the tie?

Why this matters: win rate tables are research paper gold. You will show Groq dominates technical queries (43% win rate) while Gemini excels at creative explanations (38% win rate).

---

### Category 4: Memory and Learning Signals

This is what proves your system learns:

- Similar query retrieval: for each new query, log the top 5 most similar past queries (using cosine similarity on embeddings)
- Similarity scores: what were the cosine similarity values (0.0 to 1.0)?
- Memory injection: did you actually inject these past Q&A pairs into the context of the models? Which ones?
- Cold start vs warm start: tag queries as cold start (no similar past queries with similarity > 0.7) or warm start (found relevant memory)
- Answer consistency: when someone asks what is gravity twice (weeks apart), did the answer quality improve? Track this explicitly for 50-100 repeated queries across the dataset

Why this matters: the core claim of your paper is the brain gets smarter. You will graph answer quality on cold start vs warm start queries and show a statistically significant improvement (e.g., 3.2/5 vs 4.1/5 average score).

---

### Category 5: Ground Truth and Validation

You need human evaluation on a subset:

- Random sample: every 100 queries, flag one for human review (aim for 500+ human-evaluated answers by 10K queries)
- Human quality scores: recruit 3-5 evaluators (grad students, MTurk, or Prolific) to rate answers on a 1-5 scale (1 = wrong or unhelpful, 5 = excellent)
- Inter-rater reliability: measure agreement between human evaluators (Cohen's kappa coefficient)
- Ground truth answers: for 100 factual queries, manually verify correctness (e.g., What year did WWII end? must be 1945)
- Comparison to baseline: for those same 500 queries, also get a GPT-4-only answer and a Gemini-only answer, then have humans compare (blind A/B test)

Why this matters: automated metrics are suspect. Human evaluation proves your ensemble actually produces better answers. You will write human evaluators rated ensemble answers 0.7 points higher than single-model baselines (p < 0.01).

---

### Category 6: System Behavior Metrics

Track operational data:

- Throughput: queries processed per hour
- Total cost: running sum of API costs (should stay very low with free tiers)
- Uptime: percentage of time the system was responsive
- Cache hit rate: if you implement caching (identical queries return cached answers), track how often it is used
- Gatekeeper rejection rate: what percent of queries are filtered out? (Aim for 15-25% rejection to prove the filter is working)
- Error rate: what percent of queries fail due to API errors, timeouts, or bugs?

Why this matters: practical systems need reliability data. You will include a System Performance section showing 99.2% uptime and $0.003 average cost per query.

---

### Category 7: Temporal Analysis

Track how the system evolves:

- Batch analysis: divide your 10K queries into batches of 1,000. Measure average answer quality for Batch 1 (queries 1-1000), Batch 2 (1001-2000), etc.
- Learning curve: plot average human evaluation score vs query count to show improvement over time
- Model win rate drift: did Groq's win rate increase over time as more similar queries accumulated?
- Domain emergence: track when new domains appear (e.g., first chemistry query at query 837)
- Convergence point: at what query count does improvement plateau? (Might be 3K, might be 15K)

Why this matters: the most impactful graph in your paper will be Answer Quality Over Time showing an upward trend. Reviewers will ask does it saturate and you will have data to answer.

---

## Part 2: Experimental Protocol

### Phase 1: Instrumentation (Week 1)

Before collecting any real queries:

1. Upgrade your database: add all the tables and columns listed above
2. Build logging pipeline: every API call, every decision, every timestamp gets logged automatically
3. Create admin dashboard: simple web UI showing real-time stats (queries today, win rates, costs)
4. Implement embedding storage: use sentence-transformers to generate embeddings for every query

---

### Phase 2: Seed Dataset (Week 2)

Do not wait for organic users. Actively collect diverse queries:

1. Scrape public datasets:
   - ELI5 subreddit (20,000+ questions across all domains)
   - StackOverflow (technical CS or programming questions)
   - ArXiv Q&A datasets (physics, math, biology papers)
   - Quora question dumps
   - TriviaQA or Natural Questions dataset

2. Target distribution:
   - 30% STEM (physics, math, biology, chemistry)
   - 25% Computer Science or Tech
   - 20% Humanities (history, philosophy, literature)
   - 15% General knowledge (geography, culture, current events)
   - 10% Creative (writing advice, hypotheticals, thought experiments)

3. Difficulty spread:
   - 40% simple (textbook facts)
   - 40% moderate (requires explanation)
   - 20% complex (multi-step reasoning, comparisons)

Seed data download script (example):

```python
import os
import pandas as pd

def collect_eli5(limit: int = 1000):
   import praw
   reddit = praw.Reddit(
      client_id=os.getenv("REDDIT_CLIENT_ID", ""),
      client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
      user_agent=os.getenv("REDDIT_USER_AGENT", "worldbrain_researcher"),
   )
   queries = []
   for submission in reddit.subreddit("explainlikeimfive").hot(limit=limit):
      if submission.link_flair_text == "Explained":
         title = submission.title.replace("ELI5:", "").strip()
         if title:
            queries.append({"text": title, "domain": "general", "source": "eli5"})
   return queries

df = pd.DataFrame(collect_eli5(limit=1000))
df.to_csv("seed_queries.csv", index=False)
print(f"Collected {len(df)} seed queries")
```

---

### Phase 3: Baseline Collection (Week 3)

Run your first 1,000 queries through the system:

1. No memory injection yet: disable the memory retrieval to establish a baseline
2. Pure ensemble performance: just let the 4 models compete, judge picks winners
3. Collect all 7 categories of data
4. Flag 100 queries for human evaluation: pay evaluators to rate these on Prolific ($1-2 per evaluation, budget about $300 for 100 queries times 3 evaluators)

Deliverable: baseline performance table showing each model's win rate with no memory assist.

---

### Phase 4: Learning Phase (Weeks 4-8)

Enable memory and process 4,000-9,000 more queries:

1. Turn on memory retrieval: for each query, inject top 3 similar past Q&A pairs into context
2. Process 1,000 queries per week (adjust pace based on API rate limits and costs)
3. Every 1,000 queries: generate a checkpoint analysis
   - Average human eval score for this batch
   - Model win rates
   - Cold start vs warm start performance
   - Cost analysis
4. Targeted experiments:
   - At 3,000 queries: re-run 50 queries from Batch 1 to see if answers improved
   - At 5,000 queries: run ablation (turn off memory, see if performance drops)
   - At 7,000 queries: test cross-domain transfer (does physics knowledge help biology queries?)

Deliverable: learning curve graph showing quality improvement from Batch 1 to Batch 10.

Memory threshold tuning (do this before full scale runs):

1. Take 100 random query pairs
2. Manually label as truly similar or not similar
3. Plot ROC curve for different thresholds (0.5, 0.6, 0.7, 0.8, 0.9)
4. Choose the threshold that maximizes F1 score

Typical ranges by embedder:

- sentence-transformers (all-MiniLM-L6-v2): 0.7-0.8
- OpenAI text-embedding-3-small: 0.75-0.85
- Cohere embed-english-v3.0: 0.65-0.75

Document the chosen threshold in the paper methodology section.

---

### Phase 5: Validation (Week 9)

Prove your results are real:

1. Ablation studies: re-run 500 queries with variations
   - No gatekeeper (accept all queries): measure quality drop
   - No memory: measure quality drop
   - Single model (no ensemble): compare to ensemble
   - Random selection (no judge): measure quality drop

2. Statistical testing:
   - T-test: is Batch 10 quality significantly higher than Batch 1? (p < 0.05 required)
   - ANOVA: do different domains show different learning rates?
   - Correlation: does similarity score predict answer quality improvement?

3. External validation:
   - Run 100 queries through ChatGPT, Claude, and Gemini individually
   - Have humans compare your ensemble output vs these baselines
   - Measure win rate (target: your system wins >= 40% vs GPT-4)

Deliverable: statistical proof that learning happened.

Error analysis template (add to final report):

Manually review 100 lowest-quality answers (human score <= 2) and categorize:

1. Factual errors (e.g., WWII ended in 1946)
2. Incomplete (only answered part of a multi-part question)
3. Irrelevant (off-topic tangent)
4. Contradictory (answer contradicts itself)
5. Refused (model refused when it should not)
6. Ambiguous query (user question was unclear)

Report results in the paper, for example: primary failure mode is incompleteness (38%), followed by factual errors (27%).

---

## Part 3: Minimum Viable Dataset for arXiv

### Tier 1: Bare Minimum (3,000 queries)

If you want to publish something on arXiv quickly:

- 3,000 total queries (seed dataset, not organic users)
- 300 human-evaluated (10% sample)
- 3 batches of 1,000 to show early learning trend
- Basic ablation: memory on vs off
- Cost comparison vs GPT-4 baseline

Paper strength: preliminary results or proof of concept. It will get cited but is not high impact.

---

### Tier 2: Solid Paper (5,000-7,000 queries)

This is the recommended minimum for a respectable arXiv preprint:

- 5,000-7,000 total queries
- 500+ human-evaluated (10% sample)
- 5-7 batches showing clear learning trend
- Full ablation suite (no gatekeeper, no memory, no judge, single model)
- Statistical significance testing (p-values)
- Domain-specific analysis (win rates per domain)
- Cost analysis
- Comparison to 2-3 baselines (GPT-4, Claude, Gemini)

Paper strength: conference-workshop quality. It will get accepted to NeurIPS or ICLR workshops, could be arXiv front-page material.

Detailed cost breakdown (example for 5,000 queries and 500 human evaluations):

| Item | Quantity | Unit Cost | Total |
| --- | --- | --- | --- |
| API costs | | | |
| Groq (free tier) | 5,000 calls | $0.00 | $0 |
| Gemini (free tier) | 5,000 calls | $0.00 | $0 |
| Mistral (free tier) | 5,000 calls | $0.00 | $0 |
| OpenAI GPT-3.5 | 5,000 calls x 500 tokens avg | $0.0015/1K | $3.75 |
| Judge (GPT-4o-mini) | 5,000 calls x 200 tokens avg | $0.00015/1K | $0.15 |
| Embeddings (OpenAI) | 5,000 calls x 50 tokens avg | $0.00002/1K | $0.01 |
| Human evaluation | | | |
| Prolific workers | 500 evals x 3 raters | $0.40 each | $600 |
| Attention checks | 50 evals | $0.40 each | $20 |
| Infrastructure | | | |
| PostgreSQL hosting | 3 months | $15/month | $45 |
| Domain name (optional) | 1 year | $12 | $12 |
| TOTAL | | | $680.91 |

Cost reduction strategies:

- Use only 2 human raters instead of 3 (saves about $200)
- Self-host PostgreSQL (saves $45)
- Use all free-tier models (already doing this)
- Skip attention checks (saves $20, not recommended)

Minimum budget estimate: about $435 with 2 raters and self-hosted DB.

---

### Tier 3: Conference-Ready (10,000+ queries)

If you want to submit to a top conference (ICML, NeurIPS, EMNLP):

- 10,000+ total queries
- 1,000+ human-evaluated (10% sample, multiple evaluators)
- 10 batches with clear learning curve (preferably showing saturation point)
- Full ablation suite plus cross-domain transfer experiments
- Comparison to 5+ baselines (GPT-4, Claude, Gemini, Llama-3-70B, Mixtral)
- Error analysis (what types of queries does the system fail on?)
- Reproducibility package (Docker container, dataset release, code on GitHub)
- Statistical rigor (confidence intervals, significance tests, inter-rater reliability)

Paper strength: top-tier conference submission quality. Could get into ICML or NeurIPS main track.

Reproducibility checklist (for conference submission):

- Code on GitHub with MIT or Apache 2.0 license
- Docker Compose runs on fresh Ubuntu 24.04 install
- README with step-by-step setup (tested by someone else)
- Dataset released (anonymized queries plus responses)
- API keys replaced with placeholders in .env.example
- requirements.txt with pinned versions (e.g., torch==2.1.0)
- Random seeds fixed for reproducibility (np.random.seed(42))
- Model versions documented (e.g., gpt-3.5-turbo-0125)
- Human evaluation rubric included in appendix
- Judge prompts included in code
- Analysis scripts generate all paper graphs from raw data
- Supplementary material uploaded to arXiv

Gold standard: someone can run docker compose up and replicate core results within 24 hours.

---

## Part 4: Critical Success Metrics

Your paper needs to prove 3 core claims:

### Claim 1: The ensemble outperforms single models

Required evidence:
- Head-to-head comparison table: ensemble vs GPT-4, Gemini, Claude (solo)
- Human evaluators prefer ensemble >= 40% of the time
- Statistical significance: p < 0.05 on paired t-test

---

### Claim 2: The system learns over time

Required evidence:
- Learning curve showing Batch 10 > Batch 1 (>= 15% improvement)
- Cold start vs warm start analysis (warm start answers are better)
- Repeated query test: same question asked at Query 100 vs Query 5000 gets better answer
- Statistical significance: p < 0.01 on batch comparison

---

### Claim 3: It is cost-effective and practical

Required evidence:
- Cost per query < $0.01 (vs GPT-4's about $0.02-0.05)
- Average response time < 5 seconds
- Gatekeeper filters out >= 15% junk (shows quality control works)
- Uptime > 95%

---

## Part 5: Month-by-Month Timeline

### Month 1: Infrastructure and Baseline

- Week 1: implement full logging (all 7 categories)
- Week 2: collect 1,000 seed queries from public datasets
- Week 3: run baseline experiments (no memory)
- Week 4: get 100 queries human-evaluated

Milestone: baseline performance documented.

Optional: pre-register your study (Week 1)

1. Post your experimental plan to OSF (Open Science Framework)
2. Include hypothesis, sample size, analysis plan, stopping rules
3. Timestamp it to avoid hindsight bias

Benefits: stronger credibility with reviewers and clearer methodology.

---

### Month 2: Learning Phase

- Week 5-6: process 2,000 queries with memory enabled
- Week 7: checkpoint analysis (3K queries total)
- Week 8: process 1,000 more queries plus ablation experiments

Milestone: 4,000 queries, learning curve visible.

---

### Month 3: Validation and Writing

- Week 9: final data collection push (6K-10K queries)
- Week 10: run all ablation studies plus statistical tests
- Week 11: get 500 queries human-evaluated (final validation)
- Week 12: write paper draft

Milestone: paper submitted to arXiv.

---

## Part 6: Storage and Analysis Tools

### Database Setup

```
# Upgrade from SQLite to PostgreSQL for better concurrency
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=worldbrain postgres

# Use this schema (simplified):
queries: query_id, text, timestamp, domain, complexity, accepted
responses: response_id, query_id, model, text, time_ms, cost
judge_decisions: decision_id, query_id, winner, scores, reasoning
memory: retrieval_id, query_id, similar_query_id, similarity
human_evals: eval_id, query_id, evaluator_id, score_1_to_5
```

Add a concrete schema for implementation:

```sql
CREATE TABLE queries (
   query_id SERIAL PRIMARY KEY,
   timestamp TIMESTAMP DEFAULT NOW(),
   user_id TEXT,
   query_text TEXT NOT NULL,
   query_length INT,
   embedding VECTOR(384),
   domain TEXT,
   complexity_score FLOAT,
   accepted BOOLEAN,
   rejection_reason TEXT,
   has_memory_context BOOLEAN,
   memory_context_count INT,
   processing_time_ms INT
);

CREATE TABLE model_responses (
   response_id SERIAL PRIMARY KEY,
   query_id INT REFERENCES queries(query_id),
   model_name TEXT,
   model_version TEXT,
   response_text TEXT,
   response_time_ms INT,
   token_count_input INT,
   token_count_output INT,
   cost_usd NUMERIC(10,6),
   confidence_score FLOAT,
   error_message TEXT,
   timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE judge_decisions (
   decision_id SERIAL PRIMARY KEY,
   query_id INT REFERENCES queries(query_id),
   winning_response_id INT REFERENCES model_responses(response_id),
   winning_model TEXT,
   judge_reasoning TEXT,
   accuracy_score FLOAT,
   coherence_score FLOAT,
   completeness_score FLOAT,
   total_score FLOAT,
   timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE memory_retrievals (
   retrieval_id SERIAL PRIMARY KEY,
   query_id INT REFERENCES queries(query_id),
   retrieved_query_id INT REFERENCES queries(query_id),
   similarity_score FLOAT,
   rank INT,
   was_injected BOOLEAN
);

CREATE TABLE human_evaluations (
   eval_id SERIAL PRIMARY KEY,
   query_id INT REFERENCES queries(query_id),
   response_id INT REFERENCES model_responses(response_id),
   evaluator_id TEXT,
   quality_score INT CHECK (quality_score BETWEEN 1 AND 5),
   correctness BOOLEAN,
   helpfulness_score INT,
   comments TEXT,
   timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE system_metrics (
   metric_id SERIAL PRIMARY KEY,
   timestamp TIMESTAMP DEFAULT NOW(),
   queries_processed_hour INT,
   total_cost_usd NUMERIC(10,2),
   uptime_percent FLOAT,
   error_rate_percent FLOAT,
   gatekeeper_rejection_rate FLOAT
);

CREATE INDEX idx_queries_domain ON queries(domain);
CREATE INDEX idx_queries_timestamp ON queries(timestamp);
CREATE INDEX idx_responses_model ON model_responses(model_name);
CREATE INDEX idx_memory_similarity ON memory_retrievals(similarity_score DESC);
```

Note on vector storage: if using PostgreSQL with pgvector, run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

If not using pgvector, store embeddings as JSON or in a separate vector database.

### Analysis Scripts

You will need Python scripts to generate:
- Learning curves (matplotlib: query count vs quality)
- Win rate heatmaps (seaborn: model x domain win percentages)
- Cost analysis (total cost, cost per query over time)
- Statistical tests (scipy.stats: t-tests, ANOVA, correlation)
- Similarity distribution (histogram of cosine similarities)

Example analysis script template:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Load data
queries = pd.read_sql("SELECT * FROM queries", conn)
decisions = pd.read_sql("SELECT * FROM judge_decisions", conn)
human_evals = pd.read_sql("SELECT * FROM human_evaluations", conn)

# Graph 1: learning curve
batches = queries.groupby(queries.index // 1000).agg({
   "query_id": "count"
}).reset_index()
batches["avg_quality"] = human_evals.groupby(
   human_evals["query_id"] // 1000
)["quality_score"].mean().values

plt.figure(figsize=(10, 6))
plt.plot(batches.index, batches["avg_quality"], marker="o")
plt.xlabel("Batch (1000 queries each)")
plt.ylabel("Average Human Quality Score (1-5)")
plt.title("Learning Curve: Quality Improves Over Time")
plt.savefig("learning_curve.png", dpi=300)

# Graph 2: model win rates
win_rates = decisions.groupby("winning_model").size() / len(decisions)
plt.figure(figsize=(8, 6))
win_rates.plot(kind="bar")
plt.ylabel("Win Rate")
plt.title("Model Win Rates Across All Queries")
plt.savefig("win_rates.png", dpi=300)

# Statistical test: did quality improve?
batch_1 = human_evals[human_evals["query_id"] < 1000]["quality_score"]
batch_10 = human_evals[human_evals["query_id"] >= 9000]["quality_score"]
t_stat, p_value = stats.ttest_ind(batch_10, batch_1)
print(f"Batch 10 vs Batch 1: t={t_stat:.2f}, p={p_value:.4f}")
if p_value < 0.05:
   print("Statistically significant improvement.")
```

### Visualization Dashboard

Build a simple Streamlit or Gradio dashboard showing:
- Live query count
- Current win rates (pie chart)
- Recent queries (table)
- Learning curve (updating graph)
- Cost tracker

Example dashboard queries (Streamlit):

```python
import streamlit as st
import pandas as pd

# Query 1: total queries today
today_count = pd.read_sql("""
   SELECT COUNT(*) as count
   FROM queries
   WHERE DATE(query_timestamp) = CURRENT_DATE
""", conn)

# Query 2: current win rates
win_rates = pd.read_sql("""
   SELECT winning_model,
         COUNT(*) as wins,
         ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as win_pct
   FROM judge_decisions
   GROUP BY winning_model
   ORDER BY wins DESC
""", conn)

# Query 3: average quality by batch
quality_trend = pd.read_sql("""
   SELECT
      CAST(FLOOR(q.query_id / 1000) AS INTEGER) as batch,
      AVG(h.quality_score) as avg_quality
   FROM queries q
   JOIN human_evaluations h ON q.query_id = h.query_id
   GROUP BY batch
   ORDER BY batch
""", conn)

st.metric("Queries Today", today_count["count"][0])
st.bar_chart(win_rates.set_index("winning_model")["win_pct"])
st.line_chart(quality_trend.set_index("batch"))
```

### Human Evaluation Survey Template

Use a consistent survey for Prolific or MTurk:

```markdown
# Human Evaluation Survey

Task: rate the quality of an AI-generated answer.

Question shown to user: [insert original query]
AI answer: [insert winning response]

Please rate this answer on the following criteria:

1. Correctness (1-5)
   - 1 = completely wrong or misleading
   - 3 = partially correct, some errors
   - 5 = fully accurate

2. Helpfulness (1-5)
   - 1 = useless or confusing
   - 3 = somewhat helpful
   - 5 = extremely helpful and thorough

3. Overall quality (1-5)
   - 1 = very poor
   - 3 = acceptable
   - 5 = excellent

4. Would you trust this answer? (Yes or No)

5. Optional comments: [free text]

Estimated time: 2-3 minutes per evaluation
Payment: $0.40 per evaluation (about $8-12/hour)

Attention checks (to filter out careless evaluators):

Every 10th evaluation should include an obvious test.

Question: "What is 2 + 2?"
AI answer: "The answer is clearly 17."
Correct response: rating = 1 out of 5.

If an evaluator rates this 4 out of 5 or 5 out of 5, discard all their evaluations and replace them.
Budget: 50 attention checks x $0.40 = $20 (already included in cost table).
```

---

## Part 7: Red Flags to Avoid

Do not do this:
- Collect 50,000 queries but only evaluate 20 manually (not enough validation)
- Run all queries in one day (no temporal learning signal)
- Only test on one domain (e.g., only CS questions) (not generalizable)
- Cherry-pick good results (reviewers will destroy you)
- Ignore failed queries (error analysis is critical)
- Forget to track costs (efficiency claim collapses)

Do this:
- Evaluate 10% of queries manually (500-1000 total)
- Spread queries over 4-8 weeks to show learning over time
- Include 5+ diverse domains
- Report all results (good and bad)
- Analyze failure modes (what queries does your system still fail on?)
- Track every API call's cost

---

## Final Answer: How Many Queries?

| Goal | Minimum Queries | Human Evals | Timeframe | Paper Quality |
| --- | --- | --- | --- | --- |
| Quick arXiv | 3,000 | 300 | 1 month | Proof of concept |
| Solid arXiv | 5,000-7,000 | 500 | 2 months | Workshop-tier |
| Conference submission | 10,000+ | 1,000 | 3 months | Main track quality |

My recommendation: target 5,000 queries over 6-8 weeks with 500 human evaluations. This gives you:
- Enough data for statistical significance
- Clear learning trends across 5 batches
- Cost-effective (under $500 total for APIs plus human evals)
- Timeline that keeps momentum going
- Publication-ready dataset for arXiv plus workshop submissions

Start logging everything from Query #1. You can always collect more data, but you cannot reconstruct missing data retroactively.

## Bonus: Paper Writing Template

LaTeX template: https://www.overleaf.com/latex/templates/neurips-2024/tpsbbrdqcmsh

Key sections to draft first:

1. Abstract (write this last, after you know all your results)
2. Methodology (write from this guide's Part 2)
3. Results (auto-generate graphs from analysis.py, then narrate)
4. Related work (cite 40-60 papers on ensembles, continual learning, RAG)

Target length:

- arXiv preprint: 8-12 pages
- Conference submission: 8 pages max (plus appendix)

Writing timeline:

- Week 1: Methodology + Related Work (while data is collecting)
- Week 2: Results + Discussion (after data analysis)
- Week 3: Introduction + Abstract + polish
- Week 4: Submit to arXiv, then conference 2-3 months later
