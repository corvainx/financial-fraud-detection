"""
SQLAlchemy Models for Transactions and Fraud Risk Decisions.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from backend.app.core.database import Base


class TransactionRecord(Base):
    """
    Stores historical transaction details, AI risk score, and system decision.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(String(64), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Input Transaction Features
    step = Column(Integer, default=1, nullable=False)
    type = Column(String(32), nullable=False)  # PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN
    amount = Column(Float, nullable=False)
    name_orig = Column(String(64), nullable=False)
    oldbalance_orig = Column(Float, nullable=False)
    newbalance_orig = Column(Float, nullable=False)
    name_dest = Column(String(64), nullable=False)
    oldbalance_dest = Column(Float, nullable=False)
    newbalance_dest = Column(Float, nullable=False)

    # ML Output & Decision
    risk_score = Column(Float, nullable=False)  # 0.0 to 1.0
    decision = Column(String(16), nullable=False)  # APPROVE, FLAG, BLOCK
    is_fraud_predicted = Column(Boolean, default=False, nullable=False)
    flag_reasons = Column(Text, nullable=True)  # JSON or comma-separated string explaining risk factors

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "step": self.step,
            "type": self.type,
            "amount": self.amount,
            "name_orig": self.name_orig,
            "oldbalance_orig": self.oldbalance_orig,
            "newbalance_orig": self.newbalance_orig,
            "name_dest": self.name_dest,
            "oldbalance_dest": self.oldbalance_dest,
            "newbalance_dest": self.newbalance_dest,
            "risk_score": round(self.risk_score, 4),
            "risk_percentage": f"{round(self.risk_score * 100, 2)}%",
            "decision": self.decision,
            "is_fraud_predicted": self.is_fraud_predicted,
            "flag_reasons": self.flag_reasons.split("; ") if self.flag_reasons else []
        }
