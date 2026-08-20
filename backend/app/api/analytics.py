"""
Analytics & Real-Time Dashboard Statistics Endpoint.
"""

import os
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.transaction import TransactionRecord

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("")
def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Returns aggregated KPIs, risk distributions, and model performance for the dashboard.
    """
    total = db.query(TransactionRecord).count()
    
    if total == 0:
        return {
            "total_transactions": 0,
            "total_approved": 0,
            "total_flagged": 0,
            "total_blocked": 0,
            "fraud_rate_percentage": 0.0,
            "total_volume_usd": 0.0,
            "blocked_volume_usd": 0.0,
            "risk_distribution": {
                "0-20% (Low)": 0,
                "20-40% (Guarded)": 0,
                "40-60% (Moderate)": 0,
                "60-80% (High)": 0,
                "80-100% (Critical)": 0
            },
            "recent_transactions": [],
            "model_metadata": _load_model_metadata()
        }

    approved = db.query(TransactionRecord).filter(TransactionRecord.decision == "APPROVE").count()
    flagged = db.query(TransactionRecord).filter(TransactionRecord.decision == "FLAG").count()
    blocked = db.query(TransactionRecord).filter(TransactionRecord.decision == "BLOCK").count()

    total_volume = db.query(func.sum(TransactionRecord.amount)).scalar() or 0.0
    blocked_volume = db.query(func.sum(TransactionRecord.amount)).filter(TransactionRecord.decision == "BLOCK").scalar() or 0.0

    # Risk Distribution Buckets
    r_0_20 = db.query(TransactionRecord).filter(TransactionRecord.risk_score < 0.20).count()
    r_20_40 = db.query(TransactionRecord).filter(TransactionRecord.risk_score >= 0.20, TransactionRecord.risk_score < 0.40).count()
    r_40_60 = db.query(TransactionRecord).filter(TransactionRecord.risk_score >= 0.40, TransactionRecord.risk_score < 0.60).count()
    r_60_80 = db.query(TransactionRecord).filter(TransactionRecord.risk_score >= 0.60, TransactionRecord.risk_score < 0.80).count()
    r_80_100 = db.query(TransactionRecord).filter(TransactionRecord.risk_score >= 0.80).count()

    recent_txns = db.query(TransactionRecord).order_by(desc(TransactionRecord.timestamp)).limit(10).all()

    return {
        "total_transactions": total,
        "total_approved": approved,
        "total_flagged": flagged,
        "total_blocked": blocked,
        "fraud_rate_percentage": round((blocked / total) * 100, 2),
        "total_volume_usd": round(float(total_volume), 2),
        "blocked_volume_usd": round(float(blocked_volume), 2),
        "risk_distribution": {
            "0-20% (Low)": r_0_20,
            "20-40% (Guarded)": r_20_40,
            "40-60% (Moderate)": r_40_60,
            "60-80% (High)": r_60_80,
            "80-100% (Critical)": r_80_100
        },
        "recent_transactions": [t.to_dict() for t in recent_txns],
        "model_metadata": _load_model_metadata()
    }


def _load_model_metadata():
    if os.path.exists(settings.METRICS_PATH):
        try:
            with open(settings.METRICS_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None
