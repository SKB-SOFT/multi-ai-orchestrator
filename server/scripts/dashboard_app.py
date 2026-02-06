import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Add server module to path for imports
server_path = Path(__file__).parent.parent
if str(server_path) not in sys.path:
    sys.path.insert(0, str(server_path.parent))

from server.services.report_monitor import get_monitor

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)


def _normalize_db_url(raw_url: str) -> str:
    if raw_url.startswith("postgresql+asyncpg"):
        return raw_url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)
    if raw_url.startswith("sqlite+aiosqlite"):
        return raw_url.replace("sqlite+aiosqlite", "sqlite", 1)
    return raw_url


def _resolve_sqlite_url(url: str) -> str:
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////"):
        rel_path = url.replace("sqlite:///", "", 1)
        base_dir = REPO_ROOT
        abs_path = (base_dir / rel_path).resolve()
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{abs_path.as_posix()}"
    return url


def _get_engine():
    default_db = (REPO_ROOT / "app.db").as_posix()
    raw_url = os.getenv("DATABASE_URL", f"sqlite:///{default_db}")
    url = _resolve_sqlite_url(_normalize_db_url(raw_url))
    return create_engine(url)


def _table_exists(engine, table_name: str) -> bool:
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name=:name"
                ),
                {"name": table_name},
            )
            return result.first() is not None
    except Exception:
        return False


def main():
    st.set_page_config(page_title="World Brain Dashboard", layout="wide")
    st.title("🌍 World Brain Research Dashboard")

    # Initialize report monitor
    monitor = get_monitor()

    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Live Metrics", "Research Reports", "Query Analysis"])

    engine = _get_engine()
    has_brain_responses = _table_exists(engine, "brain_responses")
    has_queries = _table_exists(engine, "queries")
    has_responses = _table_exists(engine, "responses")

    # ==================== TAB 1: LIVE METRICS ====================
    with tab1:
        # Get basic stats
        try:
            if has_brain_responses:
                total_queries = pd.read_sql(
                    "SELECT COUNT(*) as count FROM brain_responses",
                    engine,
                )
                today_count = pd.read_sql(
                    "SELECT COUNT(*) as count FROM brain_responses WHERE DATE(timestamp) = DATE('now')",
                    engine,
                )
            elif has_queries:
                total_queries = pd.read_sql(
                    "SELECT COUNT(*) as count FROM queries",
                    engine,
                )
                today_count = pd.read_sql(
                    "SELECT COUNT(*) as count FROM queries WHERE DATE(query_timestamp) = DATE('now')",
                    engine,
                )
            else:
                total_queries = pd.DataFrame({"count": [0]})
                today_count = pd.DataFrame({"count": [0]})
        except Exception:
            total_queries = pd.DataFrame({"count": [0]})
            today_count = pd.DataFrame({"count": [0]})

        # Monitor status
        status = monitor.get_status()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📊 Total Queries", status["query_count"])
        col2.metric("🎯 Next Milestone", status["next_milestone"] or "N/A")
        col3.metric("✅ Reports Ready", status["reports_generated"])
        col4.metric("⚙️ Monitor Status", "🟢 Running" if status["running"] else "🔴 Idle")

        st.divider()

        # Quality metrics
        if has_brain_responses:
            quality_data = pd.read_sql(
                """
                SELECT 
                    ROUND(AVG(confidence), 3) as avg_confidence,
                    ROUND(MIN(confidence), 3) as min_confidence,
                    ROUND(MAX(confidence), 3) as max_confidence,
                    COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*) as success_rate
                FROM brain_responses
                """,
                engine,
            )
        elif has_responses:
            quality_data = pd.read_sql(
                """
                SELECT 
                    ROUND(AVG(response_time_ms) / 1000.0, 3) as avg_response_time_s,
                    ROUND(MIN(response_time_ms) / 1000.0, 3) as min_response_time_s,
                    ROUND(MAX(response_time_ms) / 1000.0, 3) as max_response_time_s,
                    COUNT(CASE WHEN status = 'success' THEN 1 END) * 100.0 / COUNT(*) as success_rate
                FROM responses
                """,
                engine,
            )
        else:
            quality_data = pd.DataFrame()

        if not quality_data.empty:
            qd = quality_data.iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            if "avg_confidence" in qd:
                col1.metric("💯 Avg Confidence", f"{qd['avg_confidence']:.3f}")
                col2.metric("🔼 Max Confidence", f"{qd['max_confidence']:.3f}")
                col3.metric("🔽 Min Confidence", f"{qd['min_confidence']:.3f}")
            else:
                col1.metric("⏱ Avg Response", f"{qd['avg_response_time_s']:.3f}s")
                col2.metric("🔼 Max Response", f"{qd['max_response_time_s']:.3f}s")
                col3.metric("🔽 Min Response", f"{qd['min_response_time_s']:.3f}s")
            col4.metric("✨ Success Rate", f"{qd['success_rate']:.1f}%")

        st.divider()

        # Provider analysis
        st.subheader("AI Provider Performance")
        if has_brain_responses:
            provider_data = pd.read_sql(
                """
                SELECT 
                    provider,
                    COUNT(*) as usage_count,
                    ROUND(AVG(confidence), 3) as avg_confidence
                FROM brain_responses
                WHERE provider IS NOT NULL
                GROUP BY provider
                ORDER BY usage_count DESC
                """,
                engine,
            )
        elif has_responses:
            provider_data = pd.read_sql(
                """
                SELECT 
                    agent_id as provider,
                    COUNT(*) as usage_count,
                    ROUND(AVG(response_time_ms) / 1000.0, 3) as avg_response_time_s
                FROM responses
                WHERE agent_id IS NOT NULL
                GROUP BY agent_id
                ORDER BY usage_count DESC
                """,
                engine,
            )
        else:
            provider_data = pd.DataFrame()

        if not provider_data.empty:
            st.bar_chart(provider_data.set_index("provider")["usage_count"])
        else:
            st.info("No provider data yet")

    # ==================== TAB 2: RESEARCH REPORTS ====================
    with tab2:
        st.subheader("📋 Research-Ready Reports")
        
        st.markdown("""
        When data collection reaches key milestones (100, 500, 1K, 2.5K, 5K, 10K queries), 
        automated research matrices are generated and stored. These are ready for download at any time.
        """)

        st.divider()

        # Report generation status
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**Current Query Count:** {status['query_count']}")
            st.write(f"**Reports Generated:** {status['reports_generated']}")
            st.write(f"**Last Check:** {status['last_check']}")
        
        with col2:
            if st.button("🔄 Check Now", use_container_width=True):
                triggered = monitor.manual_trigger()
                if triggered:
                    st.success(f"✅ Generated {len(triggered)} new report(s)!")
                else:
                    st.info("No new milestones reached yet")
                st.rerun()

        st.divider()

        # Available reports
        st.subheader("Available Research Matrices")
        
        reports = monitor.storage.get_all_reports()
        
        if reports:
            for report in reports:
                with st.expander(
                    f"📊 **{report['phase']}** - {report['query_count']} queries "
                    f"(Generated: {report['generated_at'][:10]})"
                ):
                    # Display statistics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Success Rate", f"{report['statistics']['success_rate']}%")
                    col2.metric("Avg Confidence", f"{report['statistics']['avg_confidence']:.3f}")
                    col3.metric("Unique Queries", report['statistics']['unique_queries'])

                    st.divider()

                    # Download options
                    st.write("**Download Matrix:**")
                    file_cols = st.columns(len(report['files']))
                    
                    for idx, (format_type, filepath) in enumerate(report['files'].items()):
                        with file_cols[idx]:
                            try:
                                with open(filepath, 'rb') as f:
                                    file_data = f.read()
                                
                                # Format-specific button text and MIME type
                                button_labels = {
                                    'json': '📄 JSON',
                                    'csv': '📊 CSV',
                                    'tsv': '📋 TSV',
                                    'pdf': '📑 PDF'
                                }
                                mime_types = {
                                    'json': 'application/json',
                                    'csv': 'text/csv',
                                    'tsv': 'text/tab-separated-values',
                                    'pdf': 'application/pdf'
                                }
                                
                                filename = Path(filepath).name
                                st.download_button(
                                    label=button_labels.get(format_type, format_type.upper()),
                                    data=file_data,
                                    file_name=filename,
                                    mime=mime_types.get(format_type, 'application/octet-stream'),
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Error loading {format_type}: {e}")
        else:
            st.info("📭 No reports generated yet. Keep submitting queries to reach milestones!")

        st.divider()

        st.subheader("How This Works")
        st.markdown("""
        ✅ **Automatic Generation:** Reports are generated automatically when milestones are reached
        
        ✅ **Always Ready:** Even if you're not monitoring, reports are stored and ready to download
        
        ✅ **Multiple Formats:** JSON (raw data), CSV (spreadsheet), TSV (tabs), PDF (formatted report)
        
        ✅ **Open Source Focus:** Emphasizes data diversity and global contributions, not user count
        
        📊 **Metrics Included:**
        - Query statistics (count, success rate, confidence scores)
        - Data diversity analysis (unique queries, complexity range)
        - Provider performance comparison
        - Temporal patterns
        - Quality trends and growth metrics
        """)

    # ==================== TAB 3: QUERY ANALYSIS ====================
    with tab3:
        st.subheader("Query Analytics")
        
        # Query volume
        st.write("**Daily Query Volume**")
        if has_brain_responses:
            daily_queries = pd.read_sql(
                """
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM brain_responses
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 30
                """,
                engine,
            )
        elif has_queries:
            daily_queries = pd.read_sql(
                """
                SELECT DATE(query_timestamp) as date, COUNT(*) as count
                FROM queries
                GROUP BY DATE(query_timestamp)
                ORDER BY date DESC
                LIMIT 30
                """,
                engine,
            )
        else:
            daily_queries = pd.DataFrame()
        
        if not daily_queries.empty:
            st.line_chart(daily_queries.set_index("date")["count"])
        else:
            st.info("No query data yet")

        st.divider()

        # Recent queries
        st.write("**Recent Queries**")
        if has_brain_responses:
            recent = pd.read_sql(
                """
                SELECT 
                    substr(query, 1, 100) as query,
                    ROUND(confidence, 3) as confidence,
                    success,
                    timestamp
                FROM brain_responses
                ORDER BY timestamp DESC
                LIMIT 20
                """,
                engine,
            )
        elif has_queries:
            recent = pd.read_sql(
                """
                SELECT 
                    substr(query_text, 1, 100) as query,
                    query_type,
                    query_timestamp as timestamp
                FROM queries
                ORDER BY query_timestamp DESC
                LIMIT 20
                """,
                engine,
            )
        else:
            recent = pd.DataFrame()
        
        if not recent.empty:
            st.dataframe(recent, use_container_width=True)
        else:
            st.info("No queries recorded yet")


if __name__ == "__main__":
    main()
