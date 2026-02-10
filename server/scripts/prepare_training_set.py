import os
import json
import sqlite3
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def prepare_training_data(db_path=None, output_file="training_data.jsonl"):
    """
    Export query/response/winner triples for training a custom selector or judge.
    """
    if db_path is None:
        # Try common locations
        candidates = [
            "app.db",
            "server/data/app.db",
            "../app.db",
            "server/app.db"
        ]
        for c in candidates:
            if os.path.exists(c):
                db_path = c
                break
    
    if not db_path or not os.path.exists(db_path):
        print(f"Error: Database not found. Tried: app.db, server/data/app.db")
        return

    print(f"Using database: {db_path}")
    conn = sqlite3.connect(db_path)
    
    # Query to get all queries with their responses and the judge decision
    query = """
    SELECT 
        q.query_id, 
        q.query_text, 
        jd.winning_model,
        r.agent_id, 
        r.response_text,
        r.response_time_ms
    FROM queries q
    JOIN responses r ON q.query_id = r.query_id
    LEFT JOIN judge_decisions jd ON q.query_id = jd.query_id
    WHERE r.status = 'success'
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("No successful responses found in database.")
        return

    # Group by query_id to create training samples
    training_samples = []
    for qid, group in df.groupby('query_id'):
        query_text = group['query_text'].iloc[0]
        winner = group['winning_model'].iloc[0]
        
        provider_responses = {}
        for _, row in group.iterrows():
            provider_responses[row['agent_id']] = {
                "text": row['response_text'],
                "latency": row['response_time_ms']
            }
            
        sample = {
            "query": query_text,
            "providers": provider_responses,
            "chosen_winner": winner,
            "label": winner # This can be used for training a router
        }
        training_samples.append(sample)

    with open(output_file, "w") as f:
        for sample in training_samples:
            f.write(json.dumps(sample) + "\n")
            
    print(f"Successfully exported {len(training_samples)} training samples to {output_file}")

if __name__ == "__main__":
    prepare_training_data()
