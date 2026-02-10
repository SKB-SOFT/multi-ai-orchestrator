import os
import sqlite3
import pandas as pd
import re
from pathlib import Path
from dotenv import load_dotenv

def _normalize_db_url(raw_url: str) -> str:
    if raw_url.startswith("sqlite+aiosqlite"):
        return raw_url.replace("sqlite+aiosqlite", "sqlite", 1)
    return raw_url

def detect_opinion(text):
    text = text.lower()
    if re.search(r'\byes\b', text) or re.search(r'\btrue\b', text) or re.search(r'\bagree\b', text):
        return "positive"
    if re.search(r'\bno\b', text) or re.search(r'\bfalse\b', text) or re.search(r'\bdisagree\b', text):
        return "negative"
    return "uncertain"

def main():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL", "sqlite:///../data/app.db")
    db_url = _normalize_db_url(db_url)
    
    # Try to resolve path
    if "sqlite" in db_url:
        db_path = db_url.replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            potential_path = Path(__file__).resolve().parent.parent / db_path
            if potential_path.exists():
                db_path = str(potential_path)
    else:
        print("This script currently supports SQLite for analysis.")
        return

    conn = sqlite3.connect(db_path)
    
    # Get queries with multiple successful responses
    df = pd.read_sql_query("""
        SELECT q.query_id, q.query_text, r.agent_id, r.response_text, r.response_id
        FROM queries q
        JOIN responses r ON q.query_id = r.query_id
        WHERE r.status = 'success'
    """, conn)
    
    if df.empty:
        print("No successful responses found.")
        return

    # Add opinion detection
    df['opinion'] = df['response_text'].apply(detect_opinion)
    
    # Group by query
    grouped = df.groupby('query_id')
    contradictions = 0
    total_multi_provider = 0
    
    results = []

    for q_id, group in grouped:
        if len(group) < 2:
            continue
        
        total_multi_provider += 1
        opinions = group['opinion'].tolist()
        unique_opinions = set([o for o in opinions if o != "uncertain"])
        
        is_contradiction = len(unique_opinions) > 1
        if is_contradiction:
            contradictions += 1
            
        # Get consensus (majority vote)
        valid_ops = [o for o in opinions if o != "uncertain"]
        consensus = max(set(valid_ops), key=valid_ops.count) if valid_ops else "uncertain"
        
        # Link to human evaluation if exists
        eval_q = f"SELECT quality_score, correctness FROM human_evaluations WHERE query_id = {q_id} LIMIT 1"
        human_eval = pd.read_sql_query(eval_q, conn)
        
        results.append({
            "query_id": q_id,
            "has_contradiction": is_contradiction,
            "consensus": consensus,
            "human_score": human_eval['quality_score'].iloc[0] if not human_eval.empty else None,
            "human_correct": human_eval['correctness'].iloc[0] if not human_eval.empty else None
        })

    res_df = pd.DataFrame(results)
    
    print("--- Contradiction Detection Analysis ---")
    print(f"Total Queries with Multiple Responses: {total_multi_provider}")
    print(f"Detected Contradictions (Yes/No splits): {contradictions}")
    print(f"Contradiction Rate: {(contradictions/total_multi_provider*100):.1f}%" if total_multi_provider > 0 else "N/A")
    
    if not res_df.empty and res_df['human_score'].notnull().any():
        print("\nMatch with Human Evaluation:")
        # Analyze if consensus leads to higher quality
        avg_quality_consensus = res_df[res_df['consensus'] != 'uncertain']['human_score'].mean()
        avg_quality_no_consensus = res_df[res_df['consensus'] == 'uncertain']['human_score'].mean()
        
        print(f"Avg Human Quality when consensus reached: {avg_quality_consensus:.2f}")
        print(f"Avg Human Quality when no consensus: {avg_quality_no_consensus:.2f}")

    print("\nCore finding: Turns judge weakness (conflicting answers) into a finding for V2 RL justification.")

if __name__ == "__main__":
    main()
