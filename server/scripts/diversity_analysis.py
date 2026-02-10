import os
import json
import sqlite3
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

# Mock embedding if sentence-transformers not available in this script context
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

def _normalize_db_url(raw_url: str) -> str:
    if raw_url.startswith("sqlite+aiosqlite"):
        return raw_url.replace("sqlite+aiosqlite", "sqlite", 1)
    return raw_url

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def main():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL", "sqlite:///../data/app.db")
    db_url = _normalize_db_url(db_url)
    
    # Try to resolve path
    if "sqlite" in db_url:
        db_path = db_url.replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            # Check relative to root
            potential_path = Path(__file__).resolve().parent.parent / db_path
            if potential_path.exists():
                db_path = str(potential_path)
    else:
        print("This script currently supports SQLite for analysis.")
        return

    conn = sqlite3.connect(db_path)
    
    print("Fetching provider responses...")
    query = """
    SELECT q.query_id, r.agent_id, r.response_text
    FROM queries q
    JOIN responses r ON q.query_id = r.query_id
    WHERE r.status = 'success' AND r.response_text IS NOT NULL AND r.response_text != ''
    """
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No successful responses found for analysis.")
        return

    providers = df['agent_id'].unique()
    print(f"Found responses from providers: {providers}")

    if not HAS_SENTENCE_TRANSFORMERS:
        print("Skipping embedding calculation: sentence-transformers not installed.")
        return

    model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    print(f"Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)

    # Group by query_id to get pairwise comparisons within same query
    grouped = df.groupby('query_id')
    
    matrix_sum = np.zeros((len(providers), len(providers)))
    matrix_count = np.zeros((len(providers), len(providers)))
    
    provider_to_idx = {p: i for i, p in enumerate(providers)}

    print("Computing pairwise similarities...")
    for q_id, group in grouped:
        if len(group) < 2:
            continue
            
        texts = group['response_text'].tolist()
        p_ids = group['agent_id'].tolist()
        embeddings = model.encode(texts)
        
        for i in range(len(p_ids)):
            for j in range(len(p_ids)):
                if i == j:
                    sim = 1.0
                else:
                    sim = cosine_similarity(embeddings[i], embeddings[j])
                
                idx_i = provider_to_idx[p_ids[i]]
                idx_j = provider_to_idx[p_ids[j]]
                
                matrix_sum[idx_i, idx_j] += sim
                matrix_count[idx_i, idx_j] += 1

    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        avg_matrix = matrix_sum / matrix_count
        avg_matrix = np.nan_to_num(avg_matrix)

    print("\nPairwise Similarity Matrix (Cosine Similarity):")
    sim_df = pd.DataFrame(avg_matrix, index=providers, columns=providers)
    print(sim_df)

    # Disagreement is 1 - Similarity
    disagreement_matrix = 1 - avg_matrix
    dis_df = pd.DataFrame(disagreement_matrix, index=providers, columns=providers)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(dis_df, annot=True, cmap="YlOrRd", fmt=".3f")
    plt.title("Provider Disagreement Matrix (1 - Cosine Similarity)")
    plt.ylabel("Provider A")
    plt.xlabel("Provider B")
    
    output_path = "provider_disagreement_heatmap.png"
    plt.savefig(output_path)
    print(f"\nHeatmap saved to {output_path}")
    
    # Proving "diversity -> emergent quality"
    avg_disagreement = np.mean(disagreement_matrix[np.triu_indices(len(providers), k=1)])
    print(f"\nAverage Pairwise Disagreement: {avg_disagreement:.4f}")
    print("A higher disagreement score (closer to 1.0) indicates greater response diversity, which feeds synthesis quality.")

if __name__ == "__main__":
    main()
