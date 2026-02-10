import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, UniqueConstraint, JSON, text, Index
from sqlalchemy.sql import func
from dotenv import load_dotenv

try:
    from pgvector.sqlalchemy import Vector
except Exception:
    Vector = None

_ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(_ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///../data/app.db")

# Use aiosqlite for async SQLite support
if "sqlite" in DATABASE_URL and "aiosqlite" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite:///")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# ==================== MODELS ====================

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    is_admin = Column(Boolean, default=False)
    signup_date = Column(DateTime, default=func.now())
    quota_daily = Column(Integer, default=50)
    theme = Column(String, default='dark')
    consent_research = Column(Boolean, default=True)
    anonymize_data = Column(Boolean, default=False)

class Query(Base):
    __tablename__ = "queries"

    __table_args__ = (
        Index("idx_query_domain_timestamp", "domain", "query_timestamp"),
        Index("idx_query_accepted_timestamp", "accepted", "query_timestamp"),
    )
    
    query_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    query_timestamp = Column(DateTime, default=func.now(), index=True)
    query_type = Column(String, default="general")

    query_length = Column(Integer)
    word_count = Column(Integer)
    question_type = Column(String)
    complexity_score = Column(Float)
    gatekeeper_score = Column(Float)
    domain = Column(String)
    accepted = Column(Boolean, default=True)
    rejection_reason = Column(String)
    session_id = Column(String)
    region = Column(String)
    has_memory_context = Column(Boolean, default=False)
    memory_context_count = Column(Integer, default=0)
    cold_start = Column(Boolean, default=True)
    processing_time_ms = Column(Float)
    if Vector is not None:
        embedding = Column(Vector(384))
    else:
        embedding = Column(JSON)

class Response(Base):
    __tablename__ = "responses"
    
    response_id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("queries.query_id"), nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    model_version = Column(String)
    response_text = Column(Text)
    response_time_ms = Column(Float)
    token_count = Column(Integer)
    token_count_input = Column(Integer)
    token_count_output = Column(Integer)
    cost_usd = Column(Float)
    confidence_score = Column(Float)
    cached = Column(Boolean, default=False)
    status = Column(String, default="success")
    error_message = Column(Text)

class Cache(Base):
    __tablename__ = "cache"

    __table_args__ = (
        UniqueConstraint("query_hash", "agent_id", "user_id", name="uq_cache_user_query_agent"),
    )
    
    cache_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    query_hash = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    response_text = Column(Text)
    created_timestamp = Column(DateTime, default=func.now())


class JudgeDecision(Base):
    __tablename__ = "judge_decisions"

    __table_args__ = (
        Index("idx_judge_model_timestamp", "winning_model", "timestamp"),
    )

    decision_id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("queries.query_id"), nullable=False, index=True)
    winning_response_id = Column(Integer, ForeignKey("responses.response_id"))
    winning_model = Column(String)
    judge_reasoning = Column(Text)
    accuracy_score = Column(Float)
    coherence_score = Column(Float)
    completeness_score = Column(Float)
    total_score = Column(Float)
    tie_breaker = Column(String)
    timestamp = Column(DateTime, default=func.now())


class MemoryRetrieval(Base):
    __tablename__ = "memory_retrievals"

    retrieval_id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("queries.query_id"), nullable=False, index=True)
    retrieved_query_id = Column(Integer, ForeignKey("queries.query_id"), nullable=False, index=True)
    similarity_score = Column(Float)
    rank = Column(Integer)
    was_injected = Column(Boolean, default=False)


class HumanEvaluation(Base):
    __tablename__ = "human_evaluations"

    eval_id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("queries.query_id"), nullable=False, index=True)
    response_id = Column(Integer, ForeignKey("responses.response_id"))
    evaluator_id = Column(String)
    quality_score = Column(Integer)
    correctness = Column(Boolean)
    helpfulness_score = Column(Integer)
    comments = Column(Text)
    timestamp = Column(DateTime, default=func.now())


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=func.now())
    queries_processed_hour = Column(Integer)
    total_cost_usd = Column(Float)
    uptime_percent = Column(Float)
    error_rate_percent = Column(Float)
    gatekeeper_rejection_rate = Column(Float)

# ==================== DATABASE INITIALIZATION ====================

async def init_db():
    """Create all tables"""
    async with engine.begin() as conn:
        if "postgresql" in DATABASE_URL and Vector is not None:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        yield session
