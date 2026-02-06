"""Report generator for research data collection milestones.

Generates comprehensive matrices when thresholds are hit.
Stores reports for download without requiring active monitoring.
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_db_path(db_path: Optional[str]) -> str:
    if db_path:
        return db_path
    raw_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    if raw_url.startswith("sqlite+aiosqlite"):
        raw_url = raw_url.replace("sqlite+aiosqlite", "sqlite", 1)
    if raw_url.startswith("sqlite"):
        url = make_url(raw_url)
        path = url.database or ""
        if not path:
            return str(REPO_ROOT / "app.db")
        if not os.path.isabs(path):
            return str((REPO_ROOT / path).resolve())
        return path
    return raw_url


class ReportGenerator:
    """Generates research-ready matrices at defined thresholds."""
    
    # Define research milestones (query count thresholds)
    THRESHOLDS = [100, 500, 1000, 2500, 5000, 10000]
    
    def __init__(self, db_path: Optional[str] = None, reports_dir: str = "data/research_reports"):
        self.db_path = _resolve_db_path(db_path)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def get_query_count(self) -> int:
        """Get total number of queries in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Try both possible table names
            try:
                cursor.execute("SELECT COUNT(*) FROM brain_responses")
            except sqlite3.OperationalError:
                try:
                    cursor.execute("SELECT COUNT(*) FROM queries")
                except sqlite3.OperationalError:
                    conn.close()
                    return 0
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            return 0
    
    def check_thresholds(self) -> Tuple[int, List[int]]:
        """Check which thresholds have been reached.
        
        Returns:
            Tuple of (current_count, list_of_thresholds_reached)
        """
        current_count = self.get_query_count()
        reached = [t for t in self.THRESHOLDS if t <= current_count]
        triggered = [t for t in reached if not self._report_exists(t)]
        return current_count, triggered
    
    def _report_exists(self, threshold: int) -> bool:
        """Check if report for threshold already exists."""
        report_path = self.reports_dir / f"research_report_{threshold}_queries.json"
        return report_path.exists()
    
    def generate_comprehensive_matrix(self, threshold: int = None) -> Dict:
        """Generate comprehensive research matrix.
        
        Args:
            threshold: Optional threshold to include in report metadata
        
        Returns:
            Dictionary with all research metrics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Try to read from brain_responses, fall back to queries
            try:
                df = pd.read_sql_query("SELECT * FROM brain_responses", conn)
            except Exception:
                try:
                    df = pd.read_sql_query("SELECT * FROM queries", conn)
                except Exception:
                    conn.close()
                    return {"status": "no_data", "message": "No tables found in database"}
            
            if df.empty:
                conn.close()
                return {"status": "no_data", "message": "No queries recorded yet"}
            
            matrix = {
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "total_queries": len(df),
                    "threshold": threshold,
                    "data_collection_phase": f"Phase {len([t for t in self.THRESHOLDS if t <= len(df)])}",
                },
                
                # Core statistics
                "statistics": {
                    "total_queries": len(df),
                    "successful_queries": int(df["success"].sum()) if "success" in df.columns else 0,
                    "success_rate": round(df["success"].mean() * 100, 2) if "success" in df.columns else 0,
                    "avg_confidence": round(df["confidence"].mean(), 3) if "confidence" in df.columns else 0,
                    "avg_response_time_ms": round(df["response_time"].mean() * 1000, 2) if "response_time" in df.columns else 0,
                },
                
                # Quality metrics
                "quality_analysis": {
                    "min_confidence": round(df["confidence"].min(), 3) if "confidence" in df.columns else 0,
                    "max_confidence": round(df["confidence"].max(), 3) if "confidence" in df.columns else 0,
                    "confidence_std_dev": round(df["confidence"].std(), 3) if "confidence" in df.columns else 0,
                    "queries_with_feedback": int(df["user_feedback"].notna().sum()) if "user_feedback" in df.columns else 0,
                    "avg_user_feedback": round(df["user_feedback"].mean(), 2) if "user_feedback" in df.columns else 0,
                },
                
                # Time-based analysis
                "temporal_analysis": {
                    "first_query": df["timestamp"].min() if "timestamp" in df.columns else None,
                    "last_query": df["timestamp"].max() if "timestamp" in df.columns else None,
                    "daily_average": round(len(df) / max(1, (
                        pd.to_datetime(df["timestamp"].max()) - 
                        pd.to_datetime(df["timestamp"].min())
                    ).days + 1), 1) if "timestamp" in df.columns else 0,
                },
                
                # Provider analysis
                "provider_performance": self._analyze_providers(df),
                
                # Brain strength metrics
                "brain_metrics": {
                    "avg_brain_strength": round(df["brain_strength"].mean(), 3) if "brain_strength" in df.columns else 0,
                    "max_brain_strength": round(df["brain_strength"].max(), 3) if "brain_strength" in df.columns else 0,
                    "brain_strength_growth": self._calculate_brain_growth(df),
                },
                
                # Data diversity (no user counting - focus on query diversity)
                "data_diversity": {
                    "unique_queries": len(df["query"].unique()) if "query" in df.columns else 0,
                    "query_length_avg": round(df["query"].str.len().mean(), 1) if "query" in df.columns else 0,
                    "query_length_range": [
                        int(df["query"].str.len().min()),
                        int(df["query"].str.len().max())
                    ] if "query" in df.columns else [0, 0],
                },
                
                # Response analysis
                "response_analysis": {
                    "response_length_avg": round(df["answer"].str.len().mean(), 1) if "answer" in df.columns else 0,
                    "response_length_range": [
                        int(df["answer"].str.len().min()),
                        int(df["answer"].str.len().max())
                    ] if "answer" in df.columns else [0, 0],
                },
                
                # Error tracking (without identifying users)
                "error_metrics": {
                    "failed_queries": len(df[df["success"] == False]) if "success" in df.columns else 0,
                    "error_rate_percent": round((1 - df["success"].mean()) * 100, 2) if "success" in df.columns else 0,
                },
            }
            
            conn.close()
            return matrix
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _analyze_providers(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by provider."""
        providers_data = {}
        
        if "providers_used" not in df.columns:
            return providers_data
        
        # Extract and count providers
        all_providers = []
        for providers_json in df["providers_used"]:
            try:
                if isinstance(providers_json, str):
                    providers = json.loads(providers_json)
                    all_providers.extend(providers if isinstance(providers, list) else [providers])
            except:
                pass
        
        # Aggregate by provider
        from collections import Counter
        provider_counts = Counter(all_providers)
        
        for provider, count in provider_counts.most_common():
            resp_subset = df[df["providers_used"].str.contains(provider, na=False)]
            providers_data[provider] = {
                "times_used": count,
                "success_rate": round(resp_subset["success"].mean() * 100, 2) if "success" in resp_subset.columns else 0,
                "avg_confidence": round(resp_subset["confidence"].mean(), 3) if "confidence" in resp_subset.columns else 0,
            }
        
        return providers_data
    
    def _calculate_brain_growth(self, df: pd.DataFrame) -> float:
        """Calculate brain strength growth trend."""
        if "brain_strength" not in df.columns or len(df) < 2:
            return 0.0
        
        first_half = df["brain_strength"].head(len(df) // 2).mean()
        second_half = df["brain_strength"].tail(len(df) // 2).mean()
        
        if first_half == 0:
            return 0.0
        
        growth = ((second_half - first_half) / first_half) * 100
        return round(growth, 2)
    
    def save_report(self, matrix: Dict, threshold: int = None) -> str:
        """Save report as JSON.
        
        Returns:
            Path to saved report
        """
        if threshold is None:
            threshold = matrix.get("metadata", {}).get("total_queries", "custom")
        
        filename = f"research_report_{threshold}_queries.json"
        filepath = self.reports_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(matrix, f, indent=2)
        
        return str(filepath)
    
    def generate_csv_matrix(self, threshold: int = None) -> str:
        """Generate downloadable CSV matrix.
        
        Returns:
            Path to CSV file
        """
        matrix = self.generate_comprehensive_matrix(threshold)
        
        # Flatten nested structure for CSV
        flat_data = {}
        for key, value in matrix.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    flat_data[f"{key}_{subkey}"] = subvalue
            else:
                flat_data[key] = value
        
        df = pd.DataFrame([flat_data])
        
        if threshold is None:
            threshold = matrix.get("metadata", {}).get("total_queries", "custom")
        
        filename = f"research_matrix_{threshold}_queries.csv"
        filepath = self.reports_dir / filename
        
        df.to_csv(filepath, index=False)
        return str(filepath)
    
    def get_all_reports(self) -> List[Dict]:
        """Get list of all generated reports with metadata."""
        reports = []
        
        for json_file in sorted(self.reports_dir.glob("research_report_*.json")):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    reports.append({
                        "filename": json_file.name,
                        "path": str(json_file),
                        "queries": data.get("metadata", {}).get("total_queries", 0),
                        "generated_at": data.get("metadata", {}).get("generated_at", ""),
                        "phase": data.get("metadata", {}).get("data_collection_phase", ""),
                    })
            except Exception as e:
                print(f"Error reading {json_file}: {e}")
        
        return reports
    
    def get_latest_report(self) -> Dict:
        """Get the latest generated report."""
        reports = self.get_all_reports()
        return reports[-1] if reports else None
    
    def trigger_milestone_reports(self) -> List[Dict]:
        """Check thresholds and generate reports if needed.
        
        Returns:
            List of newly generated reports
        """
        current_count, triggered = self.check_thresholds()
        generated = []
        
        for threshold in triggered:
            matrix = self.generate_comprehensive_matrix(threshold)
            self.save_report(matrix, threshold)
            self.generate_csv_matrix(threshold)
            
            generated.append({
                "threshold": threshold,
                "generated_at": datetime.utcnow().isoformat(),
                "query_count": current_count,
            })
        
        return generated
