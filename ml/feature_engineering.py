"""
Feature Engineering & Transformation Pipeline for Financial Fraud Detection.
Transforms raw transaction fields into cybersecurity domain features and ML-ready tensors.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline


class FinancialDomainFeatures(BaseEstimator, TransformerMixin):
    """
    Custom Scikit-Learn Transformer to calculate domain-specific cybersecurity & fraud indicators.
    """
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # Create a copy to prevent mutating the original DataFrame
        df = X.copy()
        
        # Ensure correct numeric types
        for col in ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest', 'step']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # 1. Balance Error Origin: (newbalanceOrig + amount) - oldbalanceOrg
        # In legitimate transfers, new_balance = old_balance - amount -> error is 0.
        df['error_balance_orig'] = (df['newbalanceOrig'] + df['amount']) - df['oldbalanceOrg']

        # 2. Balance Error Destination: (oldbalanceDest + amount) - newbalanceDest
        # In legitimate transfers, new_dest = old_dest + amount -> error is 0.
        df['error_balance_dest'] = (df['oldbalanceDest'] + df['amount']) - df['newbalanceDest']

        # 3. Transfer Ratio: Fraction of sender's balance transferred
        df['transfer_ratio'] = df['amount'] / (df['oldbalanceOrg'] + 1.0)

        # 4. Account Emptying Flag: Did this transaction completely drain the sender's account?
        df['is_draining_balance'] = ((df['newbalanceOrig'] == 0.0) & (df['amount'] > 0)).astype(float)

        # 5. Hour of day (from simulation step)
        if 'step' in df.columns:
            df['hour_of_day'] = (df['step'] % 24).astype(float)
        else:
            df['hour_of_day'] = 12.0

        # 6. Night-time transaction flag (1 AM - 5 AM)
        df['is_night_txn'] = ((df['hour_of_day'] >= 1) & (df['hour_of_day'] <= 5)).astype(float)

        # 7. Destination is Merchant Flag (starts with 'M')
        if 'nameDest' in df.columns:
            df['is_merchant_dest'] = df['nameDest'].astype(str).str.startswith('M').astype(float)
        else:
            df['is_merchant_dest'] = 0.0

        # 8. High Value Flag (> $10,000 threshold)
        df['is_high_value'] = (df['amount'] >= 10000.0).astype(float)

        return df


def build_preprocessor() -> Pipeline:
    """
    Builds the complete feature extraction and preprocessing pipeline.
    """
    categorical_features = ['type']
    numeric_features = [
        'amount',
        'oldbalanceOrg',
        'newbalanceOrig',
        'oldbalanceDest',
        'newbalanceDest',
        'error_balance_orig',
        'error_balance_dest',
        'transfer_ratio',
        'is_draining_balance',
        'hour_of_day',
        'is_night_txn',
        'is_merchant_dest',
        'is_high_value'
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', StandardScaler(), numeric_features)
        ],
        remainder='drop'
    )

    full_feature_pipeline = Pipeline([
        ('domain_features', FinancialDomainFeatures()),
        ('encoder_scaler', preprocessor)
    ])

    return full_feature_pipeline


if __name__ == "__main__":
    from dataset_generator import generate_financial_dataset
    df_sample = generate_financial_dataset(n_samples=5)
    pipeline = build_preprocessor()
    transformed = pipeline.fit_transform(df_sample)
    print("✅ Feature Pipeline test successful! Transformed shape:", transformed.shape)
