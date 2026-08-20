"""
Inference Service & Cybersecurity Decision Engine.
Loads serialized ML model, calculates fraud risk probabilities, and outputs actionable decisions.
"""

import os
import uuid
from typing import Dict, Any, List
import joblib
import pandas as pd

from backend.app.core.config import settings
from backend.app.schemas.transaction import TransactionCreate


class FraudInferenceEngine:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FraudInferenceEngine, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """
        Loads the trained ML pipeline from disk.
        If not found, triggers training automatically.
        """
        if not os.path.exists(settings.MODEL_PATH):
            print(f"⚠️ Model artifact not found at {settings.MODEL_PATH}. Training model now...")
            from ml.train import train_and_benchmark
            train_and_benchmark()

        print(f"🧠 Loading ML model from {settings.MODEL_PATH}...")
        self._model = joblib.load(settings.MODEL_PATH)
        print("✅ ML Model loaded successfully into memory.")

    def evaluate_transaction(self, txn: TransactionCreate) -> Dict[str, Any]:
        """
        Takes a transaction input, prepares features, runs inference, and returns risk & decision.
        """
        # Convert Pydantic model to DataFrame with column names expected by ML pipeline
        data_dict = {
            'step': [txn.step],
            'type': [txn.type.upper()],
            'amount': [float(txn.amount)],
            'nameOrig': [txn.name_orig],
            'oldbalanceOrg': [float(txn.oldbalance_orig)],
            'newbalanceOrig': [float(txn.newbalance_orig)],
            'nameDest': [txn.name_dest],
            'oldbalanceDest': [float(txn.oldbalance_dest)],
            'newbalanceDest': [float(txn.newbalance_dest)]
        }
        df = pd.DataFrame(data_dict)

        # 1. Generate ML Risk Score (Probability of Fraud: 0.0 to 1.0)
        try:
            probabilities = self._model.predict_proba(df)[0]
            risk_score = float(probabilities[1])  # Class 1 = Fraud
        except Exception as e:
            print(f"Prediction fallback due to: {e}")
            risk_score = 0.05

        # 2. Rule-Based Cybersecurity Explanations
        flag_reasons: List[str] = []
        hour = txn.step % 24
        orig_err = (txn.newbalance_orig + txn.amount) - txn.oldbalance_orig

        if txn.oldbalance_orig > 0 and txn.newbalance_orig == 0:
            flag_reasons.append("Account Draining: Sender balance completely emptied to $0.00")
        
        if abs(orig_err) > 1.0:
            flag_reasons.append(f"Balance Mismatch: Origin balance discrepancy of ${abs(orig_err):,.2f}")

        if txn.amount >= 50000.0:
            flag_reasons.append(f"High-Value Anomaly: Large transaction amount of ${txn.amount:,.2f}")

        if 1 <= hour <= 5:
            flag_reasons.append(f"Off-Hours Activity: Transaction initiated at {hour:02d}:00 AM")

        if txn.type.upper() in ['TRANSFER', 'CASH_OUT'] and risk_score > 0.4:
            flag_reasons.append(f"High-Risk Channel: Fast liquidation channel ({txn.type.upper()})")

        # 3. Decision Logic (3-Tier Framework)
        if risk_score > settings.BLOCK_THRESHOLD:
            decision = "BLOCK"
            is_fraud = True
            if not flag_reasons:
                flag_reasons.append(f"Critical AI Risk Score ({risk_score*100:.1f}%) exceeds block threshold ({settings.BLOCK_THRESHOLD*100:.0f}%)")
        elif risk_score >= settings.FLAG_THRESHOLD:
            decision = "FLAG"
            is_fraud = False
            if not flag_reasons:
                flag_reasons.append(f"Moderate AI Risk Score ({risk_score*100:.1f}%) requires step-up authentication (OTP/MFA)")
        else:
            decision = "APPROVE"
            is_fraud = False
            flag_reasons.append("Normal behavioral pattern verified by AI model")

        return {
            "transaction_id": f"TXN-{uuid.uuid4().hex[:10].upper()}",
            "risk_score": round(risk_score, 4),
            "risk_percentage": f"{round(risk_score * 100, 2)}%",
            "decision": decision,
            "is_fraud_predicted": is_fraud,
            "flag_reasons": flag_reasons
        }


# Singleton engine instance
engine = FraudInferenceEngine()
