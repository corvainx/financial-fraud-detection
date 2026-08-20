# 🛡️ Sentinel: AI-Based Financial Fraud Detection Platform

An end-to-end cybersecurity and machine learning platform that detects and prevents fraudulent financial transactions in real-time.

```
Incoming Transaction ➡️ Data Processing ➡️ ML Model ➡️ Risk Score (0-100%) ➡️ Decision ➡️ Database ➡️ Dashboard
```

---

## 🌟 Key Features

1. **AI/ML Fraud Classifier**:
   - Compares **Logistic Regression**, **Random Forest**, and **Gradient Boosting** pipelines.
   - Evaluated on imbalanced metrics: **Precision, Recall, F1-Score, ROC-AUC, and PR-AUC**.
   - Automatic model selection and serialization.

2. **Cybersecurity Domain Feature Engineering**:
   - Sender & Receiver Balance Error Tracking: `(new_balance + amount) - old_balance`
   - Account Draining Flags (100% balance wipeout detection)
   - Off-Hours / Night-time Anomaly Detection (1 AM – 5 AM)
   - Transfer Velocity & Value Ratios

3. **3-Tier Decisioning Engine**:
   - **`APPROVE`** (Risk Score $< 30\%$): Low risk, instant approval.
   - **`FLAG`** ($30\% \le \text{Risk Score} \le 75\%$): Moderate risk, requires step-up authentication (OTP/MFA).
   - **`BLOCK`** (Risk Score $> 75\%$): High risk, immediate prevention.

4. **FastAPI Backend & Database Layer**:
   - RESTful endpoints for single and batch predictions.
   - **Zero-config SQLite out-of-the-box** with instant support for **MySQL** via `.env`.
   - Automatic OpenAPI/Swagger documentation at `/docs`.

5. **Modern Web Dashboard & Simulator**:
   - **Interactive Live Simulator**: Test normal and attack scenarios in real time.
   - **Real-Time Risk Gauge**: Dynamic score bar, color-coded decision badges, and AI explanation tags.
   - **KPI Metrics & Charts**: Doughnut decision breakdown, risk score histogram, and transaction audit log.

---

## 📂 Project Structure

```
fraud_det/
├── data/
│   └── raw/                      # Generated / benchmark transaction datasets
├── ml/
│   ├── dataset_generator.py      # PaySim-style synthetic transaction generator
│   ├── feature_engineering.py    # Cybersecurity domain feature pipeline
│   ├── evaluate.py               # Imbalanced metric reports & confusion matrices
│   ├── train.py                  # Model benchmark & training script
│   └── artifacts/                # Serialized model (.joblib) & metrics.json
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI routers (predict, transactions, analytics, health)
│   │   ├── core/                 # Config & database connection
│   │   ├── models/               # SQLAlchemy DB entities
│   │   ├── schemas/              # Pydantic validation schemas
│   │   └── services/             # ML inference & decision engine
│   └── main.py                   # FastAPI server entry point
├── frontend/
│   ├── index.html                # Web dashboard & transaction simulator UI
│   ├── css/style.css             # Custom styles & animations
│   └── js/app.js                 # Dynamic charts & API integration
├── tests/
│   └── test_pipeline.py          # Automated test suite
├── requirements.txt              # Project dependencies
├── run.py                        # All-in-one bootstrap & launch script
└── README.md                     # Documentation
```

---

## 🚀 Quick Start (In 3 Simple Steps)

### Step 1: Activate your Virtual Environment
- **Fish Shell**:
  ```fish
  source venv/bin/activate.fish
  ```
- **Bash / Zsh**:
  ```bash
  source venv/bin/activate
  ```
- **Windows PowerShell**:
  ```powershell
  venv\Scripts\activate
  ```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the All-in-One Launcher
```bash
python run.py
```

`run.py` automatically:
1. Generates a realistic financial transaction dataset.
2. Benchmarks and trains the machine learning models.
3. Initializes the database and seeds initial history.
4. Opens the server and Web Dashboard.

---

## 🌐 Accessing the System

- **Web Dashboard & Simulator**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

---

## 🧪 Testing the API via cURL

### 1. Test a Normal Coffee Transaction (Legitimate)
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
**Response:**
```json
{
  "transaction_id": "TXN-A1B2C3D4E5",
  "risk_score": 0.021,
  "risk_percentage": "2.1%",
  "decision": "APPROVE",
  "is_fraud_predicted": false,
  "flag_reasons": ["Normal behavioral pattern verified by AI model"]
}
```

---

### 2. Test an Account Draining Attack (Fraudulent)
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
**Response:**
```json
{
  "transaction_id": "TXN-F9E8D7C6B5",
  "risk_score": 0.965,
  "risk_percentage": "96.5%",
  "decision": "BLOCK",
  "is_fraud_predicted": true,
  "flag_reasons": [
    "Account Draining: Sender balance completely emptied to $0.00",
    "High-Value Anomaly: Large transaction amount of $95,000.00",
    "Off-Hours Activity: Transaction initiated at 03:00 AM",
    "High-Risk Channel: Fast liquidation channel (TRANSFER)"
  ]
}
```

---

## 🗄️ Database Configuration (SQLite vs. MySQL)

By default, the platform uses SQLite (`fraud_detection.db`) with zero setup.

To connect to a **MySQL** database:
1. Create a `.env` file in the project root:
   ```env
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/fraud_det
   ```
2. Restart `python run.py`. The tables will be created automatically.

---

## 🔬 Running Automated Tests
```bash
pytest tests/
```
