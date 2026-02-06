"""Research report API endpoints.

Exposes report generation, monitoring, and download functionality via REST API.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from server.services.report_monitor import get_monitor, ReportMonitor

router = APIRouter(prefix="/api/research", tags=["research"])


@router.get("/status")
def get_report_status() -> Dict:
    """Get current report monitoring status."""
    try:
        monitor = get_monitor()
        return monitor.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-thresholds")
def check_thresholds() -> Dict:
    """Manually check for threshold triggers and generate reports."""
    try:
        monitor = get_monitor()
        generated = monitor.manual_trigger()
        
        return {
            "triggered": len(generated) > 0,
            "reports_generated": generated,
            "status": monitor.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports")
def list_reports() -> Dict:
    """List all available research reports."""
    try:
        monitor = get_monitor()
        reports = monitor.storage.get_all_reports()
        
        return {
            "count": len(reports),
            "reports": reports
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{threshold}")
def get_report(threshold: int) -> Dict:
    """Get specific report by threshold."""
    try:
        monitor = get_monitor()
        report = monitor.storage.get_report_by_threshold(threshold)
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail=f"No report found for threshold {threshold}"
            )
        
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/latest")
def get_latest_report() -> Dict:
    """Get the most recent report."""
    try:
        monitor = get_monitor()
        report = monitor.storage.get_latest_report()
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail="No reports available yet"
            )
        
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitor/start")
def start_monitor() -> Dict:
    """Start the background report monitor."""
    try:
        monitor = get_monitor()
        monitor.start()
        
        return {
            "status": "started",
            "monitor_status": monitor.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitor/stop")
def stop_monitor() -> Dict:
    """Stop the background report monitor."""
    try:
        monitor = get_monitor()
        monitor.stop()
        
        return {
            "status": "stopped",
            "monitor_status": monitor.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
