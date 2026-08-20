"""
Evaluation Module for Imbalanced Fraud Detection Classification.
Focuses on Precision, Recall, F1, ROC-AUC, PR-AUC, and Confusion Matrix.
"""

from typing import Dict, Any
import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score
)


def evaluate_model(model, X_test, y_test, model_name: str = "Classifier", threshold: float = 0.5) -> Dict[str, Any]:
    """
    Evaluates a trained classifier on test data with a configurable decision threshold.
    """
    if hasattr(model, "predict_proba"):
        y_probs = model.predict_proba(X_test)[:, 1]
    elif hasattr(model, "decision_function"):
        decision = model.decision_function(X_test)
        y_probs = 1 / (1 + np.exp(-decision))
    else:
        y_probs = model.predict(X_test)

    y_pred = (y_probs >= threshold).astype(int)

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    precision = float(precision_score(y_test, y_pred, zero_division=0))
    recall = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_test, y_probs))
    except Exception:
        roc_auc = 0.0

    try:
        pr_auc = float(average_precision_score(y_test, y_probs))
    except Exception:
        pr_auc = 0.0

    accuracy = float((tp + tn) / (tp + tn + fp + fn))

    metrics = {
        "model_name": model_name,
        "threshold": threshold,
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        },
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "total_test_samples": int(len(y_test)),
        "actual_fraud_count": int(sum(y_test))
    }

    return metrics


def print_evaluation_summary(metrics: Dict[str, Any]):
    """
    Prints a formatted summary of model performance for reports.
    """
    cm = metrics["confusion_matrix"]
    print(f"\n=======================================================")
    print(f"EVALUATION REPORT: {metrics['model_name']} (Threshold: {metrics['threshold']})")
    print(f"=======================================================")
    print(f"  - Precision (Fraud Accuracy) : {metrics['precision']*100:.2f}%")
    print(f"  - Recall (Fraud Catch Rate)  : {metrics['recall']*100:.2f}%")
    print(f"  - F1-Score                   : {metrics['f1_score']:.4f}")
    print(f"  - PR-AUC (Average Precision) : {metrics['pr_auc']:.4f}")
    print(f"  - ROC-AUC                    : {metrics['roc_auc']:.4f}")
    print(f"  - Accuracy                   : {metrics['accuracy']*100:.2f}%")
    print(f"-------------------------------------------------------")
    print(f"  Confusion Matrix Breakdown:")
    print(f"    - True Negatives  (Legitimate Approved) : {cm['true_negatives']:,}")
    print(f"    - False Positives (False Alarms)        : {cm['false_positives']:,}")
    print(f"    - False Negatives (Missed Fraud)        : {cm['false_negatives']:,}")
    print(f"    - True Positives  (Fraud Detected)      : {cm['true_positives']:,}")
    print(f"=======================================================\n")
