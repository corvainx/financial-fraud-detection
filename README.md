# AI-Based Financial Fraud Detection Platform

An end-to-end cybersecurity and machine learning platform that detects and analyzes fraudulent financial transactions in real time.

```
Incoming Transaction -> Data Preprocessing -> AI/ML Model -> Risk Score (0-100%) -> Decision -> Database -> Dashboard
```

---

## System Architecture & Features

1. **Machine Learning Pipeline**:
   - Compares **Logistic Regression**, **Random Forest**, and **Gradient Boosting** models.
   - Evaluates performance using imbalanced classification metrics: **Precision, Recall, F1-Score, ROC-AUC, and PR-AUC**.
   - Automatically saves and loads the best-performing pipeline.

2. **Cybersecurity Domain Feature Engineering**:
   - Origin and Destination Balance Error Tracking: `(new_balance + amount) - old_balance`
   - Account Draining Anomaly Detection (identifies accounts completely emptied to zero)
   - Off-Hours Activity Indicators (transactions initiated during abnormal hours)
   - High-Value and Transfer Velocity Ratios

3. **3-Tier Decision Engine**:
   - **`APPROVE`** (Risk Score < 30%): Low risk, transaction approved.
   - **`FLAG`** (30% <= Risk Score <= 75%): Moderate risk, requires step-up authentication (OTP/MFA) or manual review.
   - **`BLOCK`** (Risk Score > 75%): High risk, immediate prevention.

4. **FastAPI Backend & Database Layer**:
   - RESTful API endpoints for single and batch predictions.
   - Out-of-the-box **SQLite** database support (zero configuration required).
   - Instant compatibility with **MySQL** via `.env` configuration.
   - Auto-generated OpenAPI/Swagger documentation at `/docs`.

5. **Web Dashboard & Simulator**:
   - **Live Transaction Simulator**: Test realistic financial scenarios with one-click presets.
   - **Real-Time Risk Gauge**: Dynamic score visualization with risk reason indicators.
   - **Analytics Charts**: Decision distribution, risk score histogram, and transaction audit log.

---

## Project Structure

```
fraud_det/
├── data/
│   └── raw/                      # Transaction datasets
├── ml/
│   ├── dataset_generator.py      # PaySim-style synthetic transaction generator
│   ├── feature_engineering.py    # Domain feature extraction pipeline
│   ├── evaluate.py               # Imbalanced evaluation metrics & confusion matrices
│   ├── train.py                  # Model benchmark & training script
│   └── artifacts/                # Saved model (.joblib) & metrics.json
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI routers (predict, transactions, analytics, health)
│   │   ├── core/                 # App configuration & database connection
│   │   ├── models/               # SQLAlchemy database entities
│   │   ├── schemas/              # Pydantic validation schemas
│   │   └── services/             # Inference service & decision engine
│   └── main.py                   # FastAPI application entry point
├── frontend/
│   ├── index.html                # Web dashboard & transaction simulator UI
│   ├── css/style.css             # Styling and themes
│   └── js/app.js                 # Frontend API integration and Chart.js charts
├── tests/
│   └── test_pipeline.py          # Automated test suite
├── requirements.txt              # Project dependencies
├── run.py                        # All-in-one bootstrap & launch script
└── README.md                     # Documentation
```

---

## Quick Start Guide (All Operating Systems)

### Prerequisites
- **Python 3.10, 3.11, or 3.12** installed on your system.

---

### Windows

#### Using PowerShell (Recommended)
1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd path\to\fraud_det
   ```
2. Enable script execution (if not already enabled):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Create and activate the virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
4. Install dependencies and start the system:
   ```powershell
   pip install -r requirements.txt
   python run.py
   ```

#### Using Command Prompt (CMD)
1. Open CMD and navigate to the project directory:
   ```cmd
   cd path\to\fraud_det
   ```
2. Create and activate the virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate.bat
   ```
3. Install dependencies and start:
   ```cmd
   pip install -r requirements.txt
   python run.py
   ```

---

### macOS

1. Open Terminal and navigate to the project directory:
   ```bash
   cd path/to/fraud_det
   ```
2. Create and activate the virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies and start:
   ```bash
   pip install -r requirements.txt
   python3 run.py
   ```

---

### Linux

#### Bash / Zsh
1. Open Terminal and navigate to the project directory:
   ```bash
   cd path/to/fraud_det
   ```
2. Create and activate the virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies and start:
   ```bash
   pip install -r requirements.txt
   python3 run.py
   ```

#### Fish Shell
1. Open Terminal and navigate to the project directory:
   ```fish
   cd path/to/fraud_det
   ```
2. Create and activate the virtual environment:
   ```fish
   python3 -m venv venv
   source venv/bin/activate.fish
   ```
3. Install dependencies and start:
   ```fish
   pip install -r requirements.txt
   python3 run.py
   ```

---

## What `run.py` Does Automatically

When you run `python run.py`, the script executes the complete setup sequence:
1. Verifies if `data/raw/transactions.csv` exists; if not, generates a 25,000-record dataset modeled after PaySim.
2. Trains and benchmarks Logistic Regression, Random Forest, and Gradient Boosting models, saving the best model to `ml/artifacts/best_model.joblib`.
3. Initializes the database tables and seeds initial transactions for the audit log.
4. Starts the FastAPI server and serves the web dashboard.

---

## Accessing the Platform

Once `run.py` finishes starting:

- **Web Dashboard & Transaction Simulator**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Health Check**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

Press `Ctrl + C` in your terminal to stop the server at any time.

---

## API Testing Examples (cURL)

### 1. Test a Legitimate Coffee Transaction
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "step": 10,
       "type": "PAYMENT",
       "amount": 4.50,
       "name_orig": "C1002341",
       "oldbalance_orig": 500.00,
       "newbalance_orig": 495.50,
       "name_dest": "M9918231",
       "oldbalance_dest": 1000.00,
       "newbalance_dest": 1004.50
     }'
```

### 2. Test a Fraudulent Account Draining Attack
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "step": 3,
       "type": "TRANSFER",
       "amount": 95000.00,
       "name_orig": "C88219472",
       "oldbalance_orig": 95000.00,
       "newbalance_orig": 0.00,
       "name_dest": "C19028471",
       "oldbalance_dest": 0.00,
       "newbalance_dest": 0.00
     }'
```

---

## Database Configuration (Switching to MySQL)

By default, the platform uses SQLite (`fraud_detection.db`) with zero setup.

To switch to a **MySQL** database:
1. Create a `.env` file in the project root:
   ```env
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/fraud_det
   ```
2. Re-run `python run.py`. The tables will be initialized in your MySQL instance automatically.

---

## Running Automated Tests

To execute the test suite:
```bash
pytest tests/
```
