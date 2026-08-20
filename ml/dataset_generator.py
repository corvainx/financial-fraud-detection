"""
Dataset Generator & Loader for Financial Fraud Detection.
Generates realistic financial transaction data modeled after the PaySim benchmark.
"""

import os
import random
import numpy as np
import pandas as pd

def generate_financial_dataset(n_samples: int = 25000, fraud_ratio: float = 0.02, random_state: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic financial transaction dataset with known fraud patterns.
    
    Columns:
    - step: 1 hour unit of time (1 to 720, representing 30 days)
    - type: Transaction type (PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN)
    - amount: Transaction amount in USD
    - nameOrig: Origin account ID (e.g., C12345678)
    - oldbalanceOrg: Origin account balance before transaction
    - newbalanceOrig: Origin account balance after transaction
    - nameDest: Destination account ID (e.g., M12345678 for merchants, C12345678 for customers)
    - oldbalanceDest: Destination account balance before transaction
    - newbalanceDest: Destination account balance after transaction
    - isFraud: Ground truth label (1 = Fraud, 0 = Legitimate)
    """
    np.random.seed(random_state)
    random.seed(random_state)

    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud

    records = []

    # 1. Generate Legitimate Transactions
    types_legit = ['PAYMENT', 'CASH_OUT', 'TRANSFER', 'CASH_IN', 'DEBIT']
    weights_legit = [0.40, 0.25, 0.15, 0.15, 0.05]

    for _ in range(n_legit):
        step = int(np.random.randint(1, 720))
        hour_of_day = step % 24
        
        if hour_of_day < 6 or hour_of_day > 23:
            if np.random.rand() > 0.3:
                step = (step // 24) * 24 + int(np.random.randint(8, 21))

        txn_type = np.random.choice(types_legit, p=weights_legit)
        orig_id = f"C{np.random.randint(1000000, 9999999)}"

        if txn_type == 'PAYMENT':
            amount = round(float(np.random.exponential(scale=50) + np.random.uniform(5, 300)), 2)
            oldbalance_orig = round(float(np.random.uniform(amount * 1.1, amount * 10 + 500)), 2)
            newbalance_orig = round(oldbalance_orig - amount, 2)
            dest_id = f"M{np.random.randint(1000000, 9999999)}"
            oldbalance_dest = round(float(np.random.uniform(0, 10000)), 2)
            newbalance_dest = round(oldbalance_dest + amount, 2)

        elif txn_type == 'CASH_OUT':
            amount = round(float(np.random.uniform(20, 2500)), 2)
            oldbalance_orig = round(float(amount + np.random.uniform(50, 5000)), 2)
            newbalance_orig = round(oldbalance_orig - amount, 2)
            dest_id = f"C{np.random.randint(1000000, 9999999)}"
            oldbalance_dest = round(float(np.random.uniform(100, 20000)), 2)
            newbalance_dest = round(oldbalance_dest + amount, 2)

        elif txn_type == 'TRANSFER':
            amount = round(float(np.random.uniform(100, 8000)), 2)
            oldbalance_orig = round(float(amount + np.random.uniform(100, 15000)), 2)
            newbalance_orig = round(oldbalance_orig - amount, 2)
            dest_id = f"C{np.random.randint(1000000, 9999999)}"
            oldbalance_dest = round(float(np.random.uniform(0, 5000)), 2)
            newbalance_dest = round(oldbalance_dest + amount, 2)

        elif txn_type == 'CASH_IN':
            amount = round(float(np.random.uniform(50, 4000)), 2)
            oldbalance_orig = round(float(np.random.uniform(10, 5000)), 2)
            newbalance_orig = round(oldbalance_orig + amount, 2)
            dest_id = f"C{np.random.randint(1000000, 9999999)}"
            oldbalance_dest = round(float(np.random.uniform(1000, 50000)), 2)
            newbalance_dest = max(0.0, round(oldbalance_dest - amount, 2))

        else:  # DEBIT
            amount = round(float(np.random.uniform(10, 1000)), 2)
            oldbalance_orig = round(float(amount + np.random.uniform(20, 2000)), 2)
            newbalance_orig = round(oldbalance_orig - amount, 2)
            dest_id = f"C{np.random.randint(1000000, 9999999)}"
            oldbalance_dest = round(float(np.random.uniform(0, 5000)), 2)
            newbalance_dest = round(oldbalance_dest + amount, 2)

        records.append({
            'step': step,
            'type': txn_type,
            'amount': amount,
            'nameOrig': orig_id,
            'oldbalanceOrg': oldbalance_orig,
            'newbalanceOrig': newbalance_orig,
            'nameDest': dest_id,
            'oldbalanceDest': oldbalance_dest,
            'newbalanceDest': newbalance_dest,
            'isFraud': 0
        })

    # 2. Generate Fraudulent Transactions
    fraud_types = ['TRANSFER', 'CASH_OUT']

    for _ in range(n_fraud):
        step = int(np.random.randint(1, 720))
        if np.random.rand() > 0.4:
            step = (step // 24) * 24 + int(np.random.randint(1, 6))

        txn_type = np.random.choice(fraud_types)
        orig_id = f"C{np.random.randint(1000000, 9999999)}"
        dest_id = f"C{np.random.randint(1000000, 9999999)}"

        if np.random.rand() > 0.35:
            amount = round(float(np.random.uniform(5000, 250000)), 2)
            oldbalance_orig = amount
            newbalance_orig = 0.0
            oldbalance_dest = 0.0
            newbalance_dest = 0.0
        else:
            amount = round(float(np.random.uniform(20000, 500000)), 2)
            oldbalance_orig = round(float(amount * np.random.uniform(0.7, 1.0)), 2)
            newbalance_orig = 0.0
            oldbalance_dest = round(float(np.random.uniform(0, 1000)), 2)
            newbalance_dest = oldbalance_dest

        records.append({
            'step': step,
            'type': txn_type,
            'amount': amount,
            'nameOrig': orig_id,
            'oldbalanceOrg': oldbalance_orig,
            'newbalanceOrig': newbalance_orig,
            'nameDest': dest_id,
            'oldbalanceDest': oldbalance_dest,
            'newbalanceDest': newbalance_dest,
            'isFraud': 1
        })

    df = pd.DataFrame(records)
    df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return df


def ensure_dataset(data_path: str = "data/raw/transactions.csv", n_samples: int = 25000) -> pd.DataFrame:
    """
    Checks if dataset exists; if not, creates the directory and generates the dataset.
    """
    if os.path.exists(data_path):
        print(f"[DATA] Loading existing dataset from {data_path}")
        df = pd.read_csv(data_path)
    else:
        print(f"[DATA] Generating synthetic transaction dataset ({n_samples} records) at {data_path}...")
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        df = generate_financial_dataset(n_samples=n_samples)
        df.to_csv(data_path, index=False)
        print(f"[DATA] Dataset successfully generated and saved to {data_path}")

    fraud_count = int(df['isFraud'].sum())
    total_count = len(df)
    print(f"[DATA] Total Records: {total_count:,} | Legitimate: {total_count - fraud_count:,} | Fraud: {fraud_count:,} ({fraud_count/total_count*100:.2f}%)")
    return df


if __name__ == "__main__":
    ensure_dataset()
