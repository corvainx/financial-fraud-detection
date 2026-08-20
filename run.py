"""
Application Launcher for Sentinel AI Financial Fraud Detection Platform.

Performs:
1. Dataset verification & generation (if not present)
2. ML Model benchmarking & serialization (if not present)
3. Database initialization & seed data (if database is empty)
4. Starts FastAPI web server and Dashboard at http://127.0.0.1:8000
"""

import os
import sys
import uvicorn
import pandas as pd

from backend.app.core.config import settings
from backend.app.core.database import init_db, SessionLocal
from backend.app.models.transaction import TransactionRecord
from backend.app.schemas.transaction import TransactionCreate
from backend.app.services.inference import FraudInferenceEngine
from ml.dataset_generator import ensure_dataset
from ml.train import train_and_benchmark


def bootstrap_system():
    print("\n" + "=" * 65)
    print("SENTINEL: FINANCIAL FRAUD DETECTION PLATFORM")
    print("=" * 65)

    # 1. Check / Generate Dataset
    if not os.path.exists(settings.DATA_PATH):
        print("\n[Step 1/4] Generating transaction dataset...")
        ensure_dataset(data_path=settings.DATA_PATH, n_samples=25000)
    else:
        print(f"\n[Step 1/4] Transaction dataset verified at {settings.DATA_PATH}")

    # 2. Check / Train ML Model
    if not os.path.exists(settings.MODEL_PATH):
        print("\n[Step 2/4] Benchmarking ML models (Logistic Regression, Random Forest, GBDT)...")
        train_and_benchmark(data_path=settings.DATA_PATH, artifacts_dir=os.path.dirname(settings.MODEL_PATH))
    else:
        print(f"\n[Step 2/4] Trained ML model verified at {settings.MODEL_PATH}")

    # 3. Initialize Database & Seed Sample Records
    print(f"\n[Step 3/4] Initializing Database ({settings.DATABASE_URL.split('://')[0].upper()})...")
    init_db()

    db = SessionLocal()
    try:
        count = db.query(TransactionRecord).count()
        if count == 0:
            print("[Step 3/4] Seeding initial sample transactions into database...")
            engine = FraudInferenceEngine()
            
            df_seed = pd.read_csv(settings.DATA_PATH).head(35)
            for _, row in df_seed.iterrows():
                txn_input = TransactionCreate(
                    step=int(row['step']),
                    type=str(row['type']),
                    amount=float(row['amount']),
                    name_orig=str(row['nameOrig']),
                    oldbalance_orig=float(row['oldbalanceOrg']),
                    newbalance_orig=float(row['newbalanceOrig']),
                    name_dest=str(row['nameDest']),
                    oldbalance_dest=float(row['oldbalanceDest']),
                    newbalance_dest=float(row['newbalanceDest'])
                )
                res = engine.evaluate_transaction(txn_input)
                rec = TransactionRecord(
                    transaction_id=res["transaction_id"],
                    step=txn_input.step,
                    type=txn_input.type.upper(),
                    amount=txn_input.amount,
                    name_orig=txn_input.name_orig,
                    oldbalance_orig=txn_input.oldbalance_orig,
                    newbalance_orig=txn_input.newbalance_orig,
                    name_dest=txn_input.name_dest,
                    oldbalance_dest=txn_input.oldbalance_dest,
                    newbalance_dest=txn_input.newbalance_dest,
                    risk_score=res["risk_score"],
                    decision=res["decision"],
                    is_fraud_predicted=res["is_fraud_predicted"],
                    flag_reasons="; ".join(res["flag_reasons"])
                )
                db.add(rec)
            db.commit()
            print("[Step 3/4] Initial sample data seeded successfully.")
        else:
            print(f"[Step 3/4] Found {count} existing records in database.")
    finally:
        db.close()

    print("\n[Step 4/4] Starting FastAPI Server...")
    print("=" * 65)
    print("Dashboard UI     : http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    bootstrap_system()
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
