# Financial Fraud Detection Platform

An AI-powered system that analyzes financial transactions in real time and flags or blocks fraudulent activity before money is lost.

---

## What Does This Project Do?

When people transfer money online, banks need to know if the transaction is legitimate or if an attacker has compromised the account.

Traditional security systems rely on rigid rules (like *"block anything over $10,000"*). Attackers easily bypass these rules by sending smaller amounts or moving money at unusual hours.

This project solves that problem by using **Machine Learning**:

1. A transaction enters the system (amount, sender balance, receiver balance, time).
2. The AI model analyzes behavioral patterns (e.g., *Is the account suddenly emptied at 3 AM?*).
3. The system assigns a **Fraud Risk Score** from **0% to 100%**.
4. The system automatically makes an immediate cybersecurity decision:
   - **APPROVE** (Risk < 30%): Safe transaction. Processed immediately.
   - **FLAG** (Risk 30% – 75%): Suspicious. Triggers step-up security (like an OTP or MFA prompt).
   - **BLOCK** (Risk > 75%): High probability of fraud. Transaction stopped immediately.
5. The transaction and its decision are saved to a database and displayed on a live web dashboard.

---

## How It Works (The Core Pipeline)

```
[Incoming Transaction]
         │
         ▼
[Data Processing & Feature Extraction]
  - Calculates balance discrepancies
  - Checks if origin account was completely drained
  - Checks if transaction occurred during abnormal hours (1 AM - 5 AM)
         │
         ▼
[AI / Machine Learning Model]
  - Scans historical patterns to evaluate fraud probability
         │
         ▼
[Risk Score & Decision Engine]
  - Score < 30%   ──> APPROVE (Legitimate)
  - Score 30-75%  ──> FLAG (Ask for OTP / Review)
  - Score > 75%   ──> BLOCK (Fraud Prevented)
         │
         ▼
[Database & Web Dashboard]
  - Saves transaction to audit log
  - Updates analytics charts and KPI metrics in real time
```

---

## Quick Start (Run the Project)

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12 installed.

### 2. Setup and Run

#### Linux (Fish Shell):
```fish
source venv/bin/activate.fish
pip install -r requirements.txt
python run.py
```

#### Linux / macOS (Bash or Zsh):
```bash
source venv/bin/activate
pip install -r requirements.txt
python3 run.py
```

#### Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

#### Windows (Command Prompt):
```cmd
venv\Scripts\activate.bat
pip install -r requirements.txt
python run.py
```

---

## Using the System

Once `python run.py` is running, open your browser:

### 1. Web Dashboard: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Transaction Simulator**: Choose a preset test scenario (like a normal $4.50 coffee payment vs. an abnormal $95,000 night-time account drain) or type custom numbers to see how the AI scores the transaction in real time.
- **Analytics Charts**: View the live breakdown of approved, flagged, and blocked transactions.
- **Audit Log Table**: View, filter, and search all historical transactions and their risk scores.

### 2. API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Interactive Swagger UI for developers to test the backend API endpoints directly.

---

## Project Structure

```
fraud_det/
├── data/raw/                 # Historical transaction dataset
├── ml/
│   ├── dataset_generator.py  # Generates realistic transaction data
│   ├── feature_engineering.py# Extracts fraud indicators (balance errors, time flags)
│   ├── evaluate.py           # Calculates precision, recall, and F1-scores
│   ├── train.py              # Trains and benchmarks classification models
│   └── artifacts/            # Saved best-performing model file
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints for predictions and analytics
│   │   ├── core/             # Configuration and database connection
│   │   ├── models/           # Database table definitions
│   │   └── services/         # Inference and decision logic
│   └── main.py               # Backend server entry point
├── frontend/
│   ├── index.html            # Web dashboard user interface
│   ├── css/style.css         # Styling
│   └── js/app.js             # Live chart and simulator logic
├── tests/
│   └── test_pipeline.py      # Automated tests
├── requirements.txt          # Python dependencies
├── run.py                    # All-in-one launcher script
└── README.md                 # Project documentation
```

---

## Technology Stack

- **Machine Learning**: Python, Scikit-Learn, Pandas, NumPy, Joblib
- **Backend API**: FastAPI, Uvicorn, Pydantic
- **Database**: SQLite (default, zero configuration) / MySQL compatible via SQLAlchemy
- **Frontend**: HTML5, Tailwind CSS, Chart.js, Lucide Icons
