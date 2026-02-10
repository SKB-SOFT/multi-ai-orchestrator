"""Research report API endpoints.

Exposes report generation, monitoring, and download functionality via REST API.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
import pandas as pd
import io
from fastapi.responses import StreamingResponse
from server.services.report_monitor import get_monitor, ReportMonitor
from server.db import get_db, Query, Response, JudgeDecision, HumanEvaluation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

router = APIRouter(prefix="/api/research", tags=["research"])

@router.get("/export/csv/{filename}")
async def export_research_csv(filename: str, db: AsyncSession = Depends(get_db)):
    """
    Export paper-ready CSVs for research analysis.
    Supported: provider_matrix, complexity_analysis, brain_strength_evolution
    """
    buffer = io.StringIO()
    
    if filename == "provider_matrix":
        # Provider win rates, latency, and costs
        stmt = (
            select(
                Response.agent_id,
                func.count(Response.response_id).label("total_calls"),
                func.avg(Response.response_time_ms).label("avg_latency"),
                func.avg(Response.cost_usd).label("avg_cost")
            )
            .group_by(Response.agent_id)
        )
        result = await db.execute(stmt)
        df = pd.DataFrame([dict(row._mapping) for row in result.all()])
        df.to_csv(buffer, index=False)
        
    elif filename == "complexity_analysis":
        # Complexity vs human rating
        stmt = (
            select(
                Query.complexity_score,
                HumanEvaluation.quality_score,
                Query.domain
            )
            .join(HumanEvaluation, Query.query_id == HumanEvaluation.query_id)
        )
        result = await db.execute(stmt)
        df = pd.DataFrame([dict(row._mapping) for row in result.all()])
        df.to_csv(buffer, index=False)
        
    elif filename == "brain_strength_evolution":
        # Quality over time (batches of 100)
        stmt = (
            select(
                Query.query_id,
                HumanEvaluation.quality_score,
                Query.query_timestamp
            )
            .join(HumanEvaluation, Query.query_id == HumanEvaluation.query_id)
            .order_by(Query.query_id)
        )
        result = await db.execute(stmt)
        df = pd.DataFrame([dict(row._mapping) for row in result.all()])
        if not df.empty:
            df['batch'] = (df['query_id'] // 100).astype(int)
            evolution = df.groupby('batch')['quality_score'].mean().reset_index()
            evolution.to_csv(buffer, index=False)
        else:
            df.to_csv(buffer, index=False)
    else:
        raise HTTPException(status_code=404, detail="CSV template not found")

    buffer.seek(0)
    return StreamingResponse(
        io.BytesIO(buffer.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}.csv"}
    )


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
