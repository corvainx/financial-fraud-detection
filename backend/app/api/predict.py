"""
Prediction and Transaction Evaluation Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.transaction import TransactionRecord
from backend.app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    BatchTransactionCreate,
    BatchPredictionResponse
)
from backend.app.services.inference import FraudInferenceEngine

router = APIRouter(prefix="/predict", tags=["Prediction"])
engine = FraudInferenceEngine()


@router.post("", response_model=TransactionResponse)
def predict_single_transaction(txn: TransactionCreate, db: Session = Depends(get_db)):
    """
    Evaluates a single financial transaction through the ML pipeline,
    computes the risk score, makes a decision, and stores the record in the database.
    """
    try:
        eval_result = engine.evaluate_transaction(txn)

        # Create Database Record
        db_record = TransactionRecord(
            transaction_id=eval_result["transaction_id"],
            step=txn.step,
            type=txn.type.upper(),
            amount=txn.amount,
            name_orig=txn.name_orig,
            oldbalance_orig=txn.oldbalance_orig,
            newbalance_orig=txn.newbalance_orig,
            name_dest=txn.name_dest,
            oldbalance_dest=txn.oldbalance_dest,
            newbalance_dest=txn.newbalance_dest,
            risk_score=eval_result["risk_score"],
            decision=eval_result["decision"],
            is_fraud_predicted=eval_result["is_fraud_predicted"],
            flag_reasons="; ".join(eval_result["flag_reasons"])
        )

        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        return TransactionResponse(
            transaction_id=db_record.transaction_id,
            timestamp=db_record.timestamp,
            step=db_record.step,
            type=db_record.type,
            amount=db_record.amount,
            name_orig=db_record.name_orig,
            oldbalance_orig=db_record.oldbalance_orig,
            newbalance_orig=db_record.newbalance_orig,
            name_dest=db_record.name_dest,
            oldbalance_dest=db_record.oldbalance_dest,
            newbalance_dest=db_record.newbalance_dest,
            risk_score=db_record.risk_score,
            risk_percentage=eval_result["risk_percentage"],
            decision=db_record.decision,
            is_fraud_predicted=db_record.is_fraud_predicted,
            flag_reasons=eval_result["flag_reasons"]
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@router.post("/batch", response_model=BatchPredictionResponse)
def predict_batch_transactions(batch: BatchTransactionCreate, db: Session = Depends(get_db)):
    """
    Evaluates a batch of transactions and stores results.
    """
    results = []
    approved = 0
    flagged = 0
    blocked = 0

    for txn in batch.transactions:
        eval_result = engine.evaluate_transaction(txn)
        
        db_record = TransactionRecord(
            transaction_id=eval_result["transaction_id"],
            step=txn.step,
            type=txn.type.upper(),
            amount=txn.amount,
            name_orig=txn.name_orig,
            oldbalance_orig=txn.oldbalance_orig,
            newbalance_orig=txn.newbalance_orig,
            name_dest=txn.name_dest,
            oldbalance_dest=txn.oldbalance_dest,
            newbalance_dest=txn.newbalance_dest,
            risk_score=eval_result["risk_score"],
            decision=eval_result["decision"],
            is_fraud_predicted=eval_result["is_fraud_predicted"],
            flag_reasons="; ".join(eval_result["flag_reasons"])
        )
        db.add(db_record)
        db.flush()

        if eval_result["decision"] == "APPROVE":
            approved += 1
        elif eval_result["decision"] == "FLAG":
            flagged += 1
        else:
            blocked += 1

        results.append(TransactionResponse(
            transaction_id=db_record.transaction_id,
            timestamp=db_record.timestamp,
            step=db_record.step,
            type=db_record.type,
            amount=db_record.amount,
            name_orig=db_record.name_orig,
            oldbalance_orig=db_record.oldbalance_orig,
            newbalance_orig=db_record.newbalance_orig,
            name_dest=db_record.name_dest,
            oldbalance_dest=db_record.oldbalance_dest,
            newbalance_dest=db_record.newbalance_dest,
            risk_score=db_record.risk_score,
            risk_percentage=eval_result["risk_percentage"],
            decision=db_record.decision,
            is_fraud_predicted=db_record.is_fraud_predicted,
            flag_reasons=eval_result["flag_reasons"]
        ))

    db.commit()
    return BatchPredictionResponse(
        total_processed=len(batch.transactions),
        approved_count=approved,
        flagged_count=flagged,
        blocked_count=blocked,
        results=results
    )
