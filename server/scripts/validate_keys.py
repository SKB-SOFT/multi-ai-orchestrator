import os
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from server.orchestrator_v2 import PROVIDERS, get_key_pool_manager

async def validate_all_keys():
    print("="*60)
    print("Multi-AI Orchestrator - API Key Validator")
    print("="*60)
    
    key_pool = get_key_pool_manager()
    results = {}

    for provider_id, provider in PROVIDERS.items():
        print(f"\nChecking {provider_id.upper()}...")
        all_keys = key_pool.get_all_keys(provider_id)
        
        provider_results = []
        for i, key in enumerate(all_keys):
            # Temporarily force provider to use this specific key
            original_keys = provider.api_keys
            provider.api_keys = [key]
            provider.current_key_index = 0
            
            env_var_name = f"{provider_id.upper()}_API_KEY_{i+1}"
            print(f"  {env_var_name}: ", end="", flush=True)
            try:
                # Use a very short prompt for testing
                res = await provider.query("Hi, respond with 'OK'", timeout=20)
                if res["status"] == "success":
                    print("✅ VALID")
                    provider_results.append(True)
                else:
                    err_msg = res.get("error_message", "Unknown error")
                    err_type = res.get("error_type", "unknown")
                    print(f"❌ INVALID ({err_type}: {err_msg[:60]}...)")
                    provider_results.append(False)
            except Exception as e:
                print(f"❌ ERROR ({type(e).__name__}: {str(e)[:60]}...)")
                provider_results.append(False)
            finally:
                # Restore original keys
                provider.api_keys = original_keys
        
        results[provider_id] = provider_results

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for provider_id, res in results.items():
        valid_count = sum(1 for r in res if r)
        status = "✅ OK" if valid_count == len(res) else "⚠ PARTIAL" if valid_count > 0 else "❌ FAILED"
        print(f"{provider_id.upper():<12} | {valid_count}/{len(res)} valid | {status}")
    
    print("\nAdvice:")
    print("1. If a provider failed completely, check your .env file.")
    print("2. Ensure you didn't leave 'YOUR_KEY_HERE' placeholders.")
    print("3. Check for trailing spaces or incorrect quotes in .env.")
    print("4. Some providers (like Cerebras) might have waitlists.")

if __name__ == "__main__":
    asyncio.run(validate_all_keys())
