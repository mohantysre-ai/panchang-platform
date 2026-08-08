from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from .config import settings

class Base(DeclarativeBase):
    pass

class CalculationAudit(Base):
    __tablename__ = "calculation_audit"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    calculation_type: Mapped[str] = mapped_column(String(50))
    cache_key: Mapped[str] = mapped_column(String(500), index=True)
    payload_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

_engine = None

def get_engine():
    global _engine
    if not settings.postgres_enabled:
        return None
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine

def init_db():
    engine = get_engine()
    if engine:
        Base.metadata.create_all(engine)

def audit(kind, key, payload):
    engine = get_engine()
    if not engine:
        return
    try:
        with Session(engine) as session:
            session.add(CalculationAudit(
                calculation_type=kind,
                cache_key=key,
                payload_json=payload
            ))
            session.commit()
    except Exception:
        pass
