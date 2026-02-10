import asyncio
import aiohttp
import time
import json
import random
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# Stress test settings
API_URL = "http://127.0.0.1:8001/api/query"
QUERY_RATE_PER_HOUR = 1000
TEST_DURATION_HOURS = 1 # Set to 24 for full paper run
CONCURRENT_REQUESTS = 5

SYNTHETIC_QUERIES = [
    "Explain the concept of quantum entanglement.",
    "What are the trade-offs between SQL and NoSQL databases?",
    "Analyze the impact of the industrial revolution on modern society.",
    "Compare the performance of Llama-3 and Gemini-1.5.",
    "How does a transformer architecture work in LLMs?",
    "Describe the process of photosynthesis in detail.",
    "What's the relationship between inflation and interest rates?",
    "Evaluate the ethical implications of autonomous AI agents."
]

async def fire_query(session, query_id):
    query = random.choice(SYNTHETIC_QUERIES)
    payload = {
        "query_text": query,
        "selected_agents": ["groq", "gemini", "cerebras", "mistral"]
    }
    
    start_time = time.time()
    try:
        async with session.post(API_URL, json=payload, timeout=60) as response:
            status = response.status
            data = await response.json()
            latency = (time.time() - start_time) * 1000
            
            # Extract provider failures
            errors = data.get("errors", [])
            success = status == 200 and not errors
            
            return {
                "timestamp": datetime.now(),
                "success": success,
                "latency": latency,
                "error_count": len(errors),
                "providers": [r["agent_id"] for r in data.get("responses", [])],
                "failed_providers": [e["agent_id"] for e in errors]
            }
    except Exception as e:
        return {
            "timestamp": datetime.now(),
            "success": False,
            "latency": (time.time() - start_time) * 1000,
            "error_message": str(e),
            "error_count": 4, # Assume all failed
            "failed_providers": ["all"]
        }

async def run_stress_test():
    print(f"Starting Stress Test: {QUERY_RATE_PER_HOUR} queries/hr for {TEST_DURATION_HOURS} hour(s)")
    print(f"Targeting: {API_URL}")
    
    results = []
    start_test = time.time()
    end_test = start_test + (TEST_DURATION_HOURS * 3600)
    
    # Calculate interval for target rate
    interval = 3600 / QUERY_RATE_PER_HOUR
    
    async with aiohttp.ClientSession() as session:
        query_idx = 0
        while time.time() < end_test:
            # Run batch of concurrent requests
            batch_tasks = []
            for _ in range(CONCURRENT_REQUESTS):
                batch_tasks.append(fire_query(session, query_idx))
                query_idx += 1
                
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
            
            success_count = sum(1 for r in batch_results if r["success"])
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Batch {query_idx//CONCURRENT_REQUESTS}: {success_count}/{CONCURRENT_REQUESTS} successful")
            
            # Wait for next interval
            await asyncio.sleep(interval * CONCURRENT_REQUESTS)

    # Analysis
    df = pd.DataFrame(results)
    if df.empty:
        print("No results collected.")
        return

    print("\n--- Stress Test Results ---")
    print(f"Total Queries: {len(df)}")
    print(f"Overall Success Rate: {(df['success'].mean()*100):.2f}%")
    print(f"Avg Latency: {df['latency'].mean():.2f}ms")

    # Plot reliability over time (Survival Curve/MTBF)
    df['cumulative_success'] = df['success'].cumsum()
    df['uptime'] = df['success'].astype(int)
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['cumulative_success'])
    plt.title("System Reliability Path (Cumulative Successes)")
    plt.xlabel("Time")
    plt.ylabel("Successful Queries")
    plt.grid(True)
    plt.savefig("reliability_survival_curve.png")
    
    # Export for paper
    df.to_csv("stress_test_metrics.csv", index=False)
    print("\nMetrics exported to stress_test_metrics.csv")
    print("Survival curve saved to reliability_survival_curve.png")

if __name__ == "__main__":
    try:
        asyncio.run(run_stress_test())
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
