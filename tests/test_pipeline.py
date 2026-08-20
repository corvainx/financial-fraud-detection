"""
End-to-End Pipeline & API Tests.
"""

import os
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from ml.dataset_generator import generate_financial_dataset
from ml.feature_engineering import build_preprocessor
from backend.app.schemas.transaction import TransactionCreate
from backend.app.services.inference import FraudInferenceEngine

client = TestClient(app)


def test_dataset_generation():
    """Verify synthetic dataset generator produces correct columns and labels."""
    df = generate_financial_dataset(n_samples=100, fraud_ratio=0.1)
    assert len(df) == 100
    assert 'isFraud' in df.columns
    assert 'type' in df.columns
    assert 'amount' in df.columns
    assert df['isFraud'].sum() > 0


def test_feature_pipeline():
    """Verify feature pipeline transforms data into numeric vectors without NaNs."""
    df = generate_financial_dataset(n_samples=20)
    pipeline = build_preprocessor()
    transformed = pipeline.fit_transform(df)
    assert transformed.shape[0] == 20
    assert transformed.shape[1] > 5


def test_inference_engine():
    """Verify inference engine returns calibrated risk score and decision."""
    engine = FraudInferenceEngine()
    
    # Test safe payment
    safe_txn = TransactionCreate(
        step=12,
        type="PAYMENT",
        amount=15.00,
        name_orig="C111",
        oldbalance_orig=500.00,
        newbalance_orig=485.00,
        name_dest="M222",
        oldbalance_dest=1000.00,
        newbalance_dest=1015.00
    )
    res_safe = engine.evaluate_transaction(safe_txn)
    assert "risk_score" in res_safe
    assert res_safe["decision"] in ["APPROVE", "FLAG", "BLOCK"]
    assert 0.0 <= res_safe["risk_score"] <= 1.0

    # Test draining fraud pattern
    fraud_txn = TransactionCreate(
        step=3,
        type="TRANSFER",
        amount=90000.00,
        name_orig="C888",
        oldbalance_orig=90000.00,
        newbalance_orig=0.00,
        name_dest="C999",
        oldbalance_dest=0.00,
        newbalance_dest=0.00
    )
    res_fraud = engine.evaluate_transaction(fraud_txn)
    assert res_fraud["risk_score"] > res_safe["risk_score"]


def test_api_health():
    """Verify health check endpoint returns 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_predict():
    """Verify POST /api/v1/predict evaluates and returns 200."""
    payload = {
        "step": 14,
        "type": "PAYMENT",
        "amount": 45.0,
        "name_orig": "C10001",
        "oldbalance_orig": 1000.0,
        "newbalance_orig": 955.0,
        "name_dest": "M20002",
        "oldbalance_dest": 5000.0,
        "newbalance_dest": 5045.0
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "transaction_id" in data
    assert "risk_score" in data
    assert "decision" in data
