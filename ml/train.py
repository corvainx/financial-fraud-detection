"""
Model Training & Benchmarking Pipeline.
Trains Logistic Regression, Random Forest, and Gradient Boosting, evaluates them,
and saves the best-performing pipeline artifact.
"""

import os
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from ml.dataset_generator import ensure_dataset
from ml.feature_engineering import build_preprocessor
from ml.evaluate import evaluate_model, print_evaluation_summary


def train_and_benchmark(data_path: str = "data/raw/transactions.csv", artifacts_dir: str = "ml/artifacts"):
    """
    Main training workflow:
    1. Load/generate dataset
    2. Train/test stratified split
    3. Benchmark 3 models (Logistic Regression, Random Forest, Gradient Boosting)
    4. Pick the best model and serialize artifacts
    """
    os.makedirs(artifacts_dir, exist_ok=True)

    print("\n🚀 STEP 1: Loading & Inspecting Dataset...")
    df = ensure_dataset(data_path=data_path)

    # Features and Target
    feature_cols = ['step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig', 'nameDest', 'oldbalanceDest', 'newbalanceDest']
    X = df[feature_cols]
    y = df['isFraud']

    # Stratified Train/Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"📊 Training Set: {len(X_train):,} rows | Test Set: {len(X_test):,} rows")

    # Define Candidate Models
    models = {
        "Logistic Regression (Balanced)": LogisticRegression(
            class_weight='balanced',
            max_iter=1000,
            random_state=42
        ),
        "Random Forest Classifier": RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            class_weight='balanced_subsample',
            n_jobs=-1,
            random_state=42
        ),
        "Gradient Boosting Classifier": GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
    }

    results = []
    best_pipeline = None
    best_f1 = -1.0
    best_name = ""
    best_metrics = {}

    print("\n🚀 STEP 2: Training & Benchmarking Models...")

    for name, clf in models.items():
        print(f"\n🔄 Training {name}...")
        
        # Assemble complete end-to-end pipeline (Feature Extraction + Preprocessing + Classifier)
        pipeline = Pipeline([
            ('preprocessor', build_preprocessor()),
            ('classifier', clf)
        ])

        # Train pipeline
        pipeline.fit(X_train, y_train)

        # Evaluate on unseen test data
        metrics = evaluate_model(pipeline, X_test, y_test, model_name=name, threshold=0.5)
        print_evaluation_summary(metrics)
        results.append(metrics)

        # Track best model by F1-Score (balances precision and recall)
        if metrics["f1_score"] > best_f1:
            best_f1 = metrics["f1_score"]
            best_pipeline = pipeline
            best_name = name
            best_metrics = metrics

    # -------------------------------------------------------------
    # 3. PRINT COMPARISON LEADERBOARD
    # -------------------------------------------------------------
    print("\n=======================================================")
    print("🏆 MODEL BENCHMARK LEADERBOARD")
    print("=======================================================")
    print(f"{'Model':<32} | {'F1-Score':<8} | {'Recall':<8} | {'Precision':<10} | {'ROC-AUC':<8}")
    print("-" * 75)
    for r in sorted(results, key=lambda x: x["f1_score"], reverse=True):
        print(f"{r['model_name']:<32} | {r['f1_score']:<8.4f} | {r['recall']*100:<7.2f}% | {r['precision']*100:<9.2f}% | {r['roc_auc']:<8.4f}")
    print("=======================================================")
    print(f"✨ SELECTED BEST MODEL: {best_name} (F1 = {best_f1:.4f})")

    # -------------------------------------------------------------
    # 4. SAVE ARTIFACTS
    # -------------------------------------------------------------
    model_path = os.path.join(artifacts_dir, "best_model.joblib")
    metrics_path = os.path.join(artifacts_dir, "metrics.json")

    print(f"\n💾 Saving winning model to {model_path}...")
    joblib.dump(best_pipeline, model_path)

    metadata = {
        "selected_model": best_name,
        "metrics": best_metrics,
        "all_benchmarks": results,
        "feature_columns": feature_cols,
        "thresholds": {
            "approve_under": 0.30,
            "flag_under": 0.75,
            "block_above": 0.75
        }
    }

    with open(metrics_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Metadata saved to {metrics_path}")
    print(f"🎉 ML Training Phase Complete!\n")
    return best_pipeline, metadata


if __name__ == "__main__":
    train_and_benchmark()
