"""Background report generation system.

Monitors database and automatically generates reports when thresholds are reached.
Stores reports for download even when the system is offline.
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url
from server.services.report_generator import ReportGenerator
from server.services.report_exporter import ReportExporter

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


class ReportStorage:
    """Manages pre-generated research reports."""
    
    def __init__(self, storage_dir: str = "data/research_reports"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_dir / "metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load report metadata from disk."""
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "last_check": None,
                "reports": {},
                "status": "idle"
            }
    
    def _save_metadata(self):
        """Save report metadata to disk."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def register_report(self, threshold: int, report_data: Dict, exports: Dict) -> Dict:
        """Register a newly generated report."""
        report_info = {
            "threshold": threshold,
            "generated_at": datetime.utcnow().isoformat(),
            "query_count": report_data.get("metadata", {}).get("total_queries", 0),
            "phase": report_data.get("metadata", {}).get("data_collection_phase", ""),
            "files": exports,
            "statistics": {
                "success_rate": report_data.get("statistics", {}).get("success_rate", 0),
                "avg_confidence": report_data.get("statistics", {}).get("avg_confidence", 0),
                "unique_queries": report_data.get("data_diversity", {}).get("unique_queries", 0),
            }
        }
        
        self.metadata["reports"][str(threshold)] = report_info
        self.metadata["last_check"] = datetime.utcnow().isoformat()
        self._save_metadata()
        
        return report_info
    
    def get_all_reports(self) -> List[Dict]:
        """Get all stored reports with metadata."""
        reports = []
        for threshold, info in sorted(self.metadata.get("reports", {}).items(), 
                                     key=lambda x: int(x[0])):
            reports.append(info)
        return reports
    
    def get_latest_report(self) -> Optional[Dict]:
        """Get the most recent report."""
        reports = self.get_all_reports()
        return reports[-1] if reports else None
    
    def get_report_by_threshold(self, threshold: int) -> Optional[Dict]:
        """Get report for specific threshold."""
        return self.metadata.get("reports", {}).get(str(threshold))
    
    def cleanup_old_files(self, keep_days: int = 30):
        """Remove reports older than specified days, keep latest of each threshold."""
        cutoff = datetime.utcnow() - timedelta(days=keep_days)
        
        thresholds = {}
        for report_file in self.storage_dir.glob("research_*.json"):
            try:
                # Extract threshold from filename
                parts = report_file.stem.split('_')
                if len(parts) >= 3:
                    threshold = int(parts[2])
                    mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
                    
                    if threshold not in thresholds:
                        thresholds[threshold] = []
                    thresholds[threshold].append((report_file, mtime))
            except:
                pass
        
        # Keep latest for each threshold, delete old ones
        deleted = 0
        for threshold, files in thresholds.items():
            files.sort(key=lambda x: x[1], reverse=True)
            for report_file, mtime in files[1:]:  # Keep first, delete rest if old
                if mtime < cutoff:
                    report_file.unlink()
                    deleted += 1
        
        return deleted


class ReportMonitor:
    """Monitors database and triggers report generation at thresholds."""
    
    def __init__(self, 
                db_path: Optional[str] = None,
                check_interval: int = 60,
                auto_start: bool = False):
        resolved_db_path = _resolve_db_path(db_path)
        self.generator = ReportGenerator(resolved_db_path)
        self.exporter = ReportExporter()
        self.storage = ReportStorage()
        self.check_interval = check_interval
        self.running = False
        self._thread = None
        self.last_count = self.generator.get_query_count()
        
        if auto_start:
            self.start()
    
    def start(self):
        """Start background monitoring."""
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
            self.storage.metadata["status"] = "monitoring"
            self.storage._save_metadata()
    
    def stop(self):
        """Stop background monitoring."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.storage.metadata["status"] = "idle"
        self.storage._save_metadata()
    
    def _monitor_loop(self):
        """Background loop that checks for threshold triggers."""
        while self.running:
            try:
                current_count, triggered = self.generator.check_thresholds()
                
                if triggered:
                    for threshold in triggered:
                        self._generate_and_store(threshold)
                
                # Update last check time every interval
                self.storage.metadata["last_check"] = datetime.utcnow().isoformat()
                self.storage._save_metadata()
                
            except Exception as e:
                print(f"Error in monitor loop: {e}")
            
            time.sleep(self.check_interval)
    
    def _generate_and_store(self, threshold: int) -> Dict:
        """Generate and store reports for a threshold."""
        try:
            # Generate matrix
            matrix = self.generator.generate_comprehensive_matrix(threshold)
            
            # Export to all formats
            exports = self.exporter.save_export(matrix, threshold, format='all')
            
            # Register in storage
            report_info = self.storage.register_report(threshold, matrix, exports)
            
            print(f"✅ Generated reports for {threshold} queries: {report_info}")
            
            return report_info
            
        except Exception as e:
            print(f"❌ Error generating reports for {threshold}: {e}")
            return {}
    
    def manual_trigger(self) -> List[Dict]:
        """Manually trigger report generation check."""
        current_count, triggered = self.generator.check_thresholds()
        generated = []
        
        for threshold in triggered:
            report_info = self._generate_and_store(threshold)
            generated.append(report_info)
        
        return generated
    
    def get_status(self) -> Dict:
        """Get current monitoring status."""
        current_count = self.generator.get_query_count()
        _, next_thresholds = self.generator.check_thresholds()
        
        all_thresholds = self.generator.THRESHOLDS
        next_unmet = [t for t in all_thresholds if t > current_count]
        
        return {
            "running": self.running,
            "query_count": current_count,
            "last_check": self.storage.metadata.get("last_check"),
            "reports_generated": len(self.storage.get_all_reports()),
            "next_milestone": next_unmet[0] if next_unmet else None,
            "milestones_reached": [t for t in all_thresholds if t <= current_count],
            "pending_triggers": next_thresholds,
        }
    
    def test_report_generation(self) -> Dict:
        """Test report generation without threshold check."""
        matrix = self.generator.generate_comprehensive_matrix()
        exports = self.exporter.save_export(matrix, 0, format='all')
        return {
            "matrix": matrix,
            "exports": exports
        }


# Singleton instance (lazy loaded)
_monitor_instance: Optional[ReportMonitor] = None


def get_monitor() -> ReportMonitor:
    """Get or create the global report monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = ReportMonitor(auto_start=True)
    return _monitor_instance


def initialize_monitor(db_path: Optional[str] = None, 
                     check_interval: int = 60,
                     auto_start: bool = True):
    """Initialize the global monitor with custom settings."""
    global _monitor_instance
    _monitor_instance = ReportMonitor(
        db_path=db_path,
        check_interval=check_interval,
        auto_start=auto_start
    )
    return _monitor_instance
