# AI-Based Financial Fraud Detection Platform

An intelligent, real-time security system that analyzes financial transactions, calculates a fraud risk score using Machine Learning, and automatically stops suspicious activity before money is stolen.

---

## 1. What Is This Project? (The Simple Explanation)

Imagine a security guard standing at a bank's digital counter:
- Every time a customer sends money, the guard checks who is sending it, how much is being sent, what time it is, and whether the account balance makes sense.
- If everything looks normal (like buying coffee at 10 AM), the transaction goes through immediately.
- If something looks slightly unusual, the guard pauses the transfer and asks for an OTP verification.
- If an attacker is draining an entire bank account at 3 AM, the guard immediately **blocks** the transfer.

**This project is that digital security guard, powered by Artificial Intelligence.**

---

## 2. The Problem: Why Old Security Systems Fail

Traditional bank security relies on rigid, manual rules:
```
Rule: "If a transfer is greater than $10,000, block it."
```
**Why this fails:** Fraudsters quickly learn the rules. They will simply transfer $9,999 multiple times or steal smaller amounts across thousands of accounts.

**The Solution:** Instead of fixed rules, this project uses **Machine Learning**. The AI looks at multiple subtle clues simultaneously (timing, balance changes, account history) to spot fraud patterns that humans and simple rules miss.

---

## 3. How It Works Under the Hood (The 5-Step Pipeline)

```
[1. Incoming Transaction] 
          │
          ▼
[2. Feature Detective] ──> (Checks for balance errors, 3 AM transfers, emptied accounts)
          │
          ▼
[3. AI / ML Brain]     ──> (Compares transaction against 25,000 historical patterns)
          │
          ▼
[4. Risk Score & Decision]
          │
          ├── Score < 30%   ──> APPROVE (Low Risk, instant approval)
          ├── Score 30-75%  ──> FLAG (Medium Risk, requires OTP / MFA)
          └── Score > 75%   ──> BLOCK (High Risk, immediate prevention)
          │
          ▼
[5. Database & Web Dashboard]
          └── Saves record in audit log and updates live charts
```

### Step 1: A Transaction Arrives
A customer initiates a transfer. The system receives standard details:
- **Transaction Type**: Transfer, Cash-Out, Payment, Cash-In, or Debit.
- **Amount**: The amount being moved.
- **Sender Balance**: Balance before and after the transaction.
- **Receiver Balance**: Receiver's balance before and after.
- **Time of Day**: Hour the transaction occurred (0 to 23).

### Step 2: The Feature Detective (Domain Processing)
Before handing the data to the AI, the system calculates hidden cybersecurity indicators:
- **Account Draining Check**: Did this transaction reduce the sender's balance to exactly zero?
- **Balance Math Check**: Does `(Old Balance - Amount) == New Balance`? (Fraudulent transactions often have balance mismatches).
- **Abnormal Hours Check**: Is this happening between 1 AM and 5 AM?
- **Transfer Volume Ratio**: What percentage of the sender's total net worth is being moved in a single second?

### Step 3: The AI Model (Pattern Recognition)
The machine learning model scans the numbers. Having learned from thousands of past transactions, it calculates the mathematical probability that the transaction is fraud.

### Step 4: The 3-Tier Security Decision
The probability is converted into a **Risk Score (0% to 100%)**:
- **`APPROVE` (Score < 30%)**: Normal behavioral pattern. Transaction proceeds with zero friction.
- **`FLAG` (Score 30% – 75%)**: Moderate risk. The system flags the transfer and prompts the user for two-factor authentication (OTP/MFA).
- **`BLOCK` (Score > 75%)**: High risk. The transaction is immediately stopped, and the reason is logged.

### Step 5: Database Logging & Dashboard Display
The transaction, risk score, decision, and reasons are saved into the database and instantly rendered on the live web dashboard.

---

## 4. Machine Learning Explained in Plain English

### What is the ML Model doing?
The machine learning model is not magic; it is statistical pattern recognition. During training, the computer is shown a spreadsheet of **25,000 historical transactions**:
- 24,500 are labeled **Legitimate (0)**.
- 500 are labeled **Fraudulent (1)**.

The model learns what normal behavior looks like vs. what an attack looks like.

### Which Models are Tested?
The system automatically trains and compares three different algorithms:
1. **Logistic Regression**: A fast, baseline linear model.
2. **Random Forest**: An ensemble of 100 decision trees voting together.
3. **Gradient Boosting**: An advanced model that builds trees sequentially, each correcting the mistakes of the previous tree.

The system automatically measures which model has the highest **F1-Score and Recall** (fraud detection rate) and saves the winning model for live predictions.

---

## 5. Web Dashboard & Features

When you open the web interface, you have access to:

1. **Transaction Scoring Simulator**:
   - Test custom transaction values or select one-click presets:
     - *Point of Sale*: Normal $4.50 coffee payment.
     - *Direct Deposit*: Legitimate $3,200 salary deposit.
     - *High Transfer*: Elevated $18,000 business move.
     - *Account Drain*: Suspicious $95,000 account wipeout at 3 AM.
2. **Real-Time Risk Gauge**:
   - Visual progress bar showing exact fraud probability and human-readable explanation tags.
3. **Multi-Currency Switcher**:
   - Seamlessly toggle currency formatting between **INR (₹)**, **USD ($)**, **EUR (€)**, and **GBP (£)** across all forms, presets, and tables.
4. **Analytics Charts**:
   - Live doughnut chart of Approved vs. Flagged vs. Blocked transfers.
   - Histogram showing how risk scores are distributed.
5. **Transaction Audit Log Table**:
   - Searchable, filterable log of all evaluated transactions with timestamps and decisions.

---

## 6. How to Run the Project (Step-by-Step)

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your computer.

---

### Step 1: Open Your Terminal and Activate the Environment

- **Linux (Fish Shell)**:
  ```fish
  cd path/to/fraud_det
  source venv/bin/activate.fish
  ```

- **Linux / macOS (Bash or Zsh)**:
  ```bash
  cd path/to/fraud_det
  source venv/bin/activate
  ```

- **Windows (PowerShell)**:
  ```powershell
  cd path\to\fraud_det
  .\venv\Scripts\Activate.ps1
  ```

- **Windows (Command Prompt)**:
  ```cmd
  cd path\to\fraud_det
  venv\Scripts\activate.bat
  ```

---

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 3: Start the Platform

```bash
python run.py
```

`run.py` automatically handles everything:
1. Generates the historical transaction dataset.
2. Trains and benchmarks the AI models.
3. Saves the best model file.
4. Initializes the database and seeds initial transaction history.
5. Starts the web server.

---

### Step 4: Open in Your Browser

- **Web Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 7. Project Structure

```
fraud_det/
├── data/
│   └── raw/                  # Transaction datasets (auto-generated)
├── ml/
│   ├── dataset_generator.py  # Generates realistic PaySim financial data
│   ├── feature_engineering.py# Extracts cybersecurity domain indicators
│   ├── evaluate.py           # Calculates precision, recall, and F1 metrics
│   ├── train.py              # Trains and benchmarks ML models
│   └── artifacts/            # Stores the winning saved model (.joblib)
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI endpoints (/predict, /transactions, /analytics)
│   │   ├── core/             # Configuration and database connection
│   │   ├── models/           # Database tables (SQLAlchemy)
│   │   ├── schemas/          # Input/output data validation (Pydantic)
│   │   └── services/         # Inference engine & 3-tier decision rules
│   └── main.py               # FastAPI server application
├── frontend/
│   ├── index.html            # Web dashboard user interface
│   ├── css/style.css         # Styling and layouts
│   └── js/app.js             # Currency switcher, charts, and simulator logic
├── tests/
│   └── test_pipeline.py      # Automated test suite
├── requirements.txt          # Python dependencies
├── run.py                    # All-in-one bootstrap and launcher script
└── README.md                 # Project documentation
```

---

## 8. Technology Stack

- **Machine Learning**: Python, Scikit-Learn, Pandas, NumPy, Joblib
- **Backend API**: FastAPI, Uvicorn, Pydantic
- **Database**: SQLite (default, zero setup) / MySQL compatible via SQLAlchemy
- **Frontend Dashboard**: HTML5, Tailwind CSS, Chart.js, Lucide Icons

