# Financial Fraud Detection Platform

![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)

An intelligent, real-time system that analyzes financial transactions, scores them for fraud risk using Machine Learning, and automatically stops suspicious activity before money is stolen.

---

## Table of Contents

1. [What Is This Project?](#1-what-is-this-project)
2. [Why Old Security Systems Fail](#2-why-old-security-systems-fail)
3. [How It Works](#3-how-it-works)
4. [The Machine Learning, Explained Simply](#4-the-machine-learning-explained-simply)
5. [Model Results](#5-model-results)
6. [Web Dashboard](#6-web-dashboard)
7. [Getting Started](#7-getting-started)
8. [Project Structure](#8-project-structure)
9. [Technology Stack](#9-technology-stack)

---

## 1. What Is This Project?

Imagine a security guard standing at a bank's digital counter, watching every transaction go by:

- A customer buys coffee for $4.50 at 10 AM → looks completely normal → **waved through instantly**.
- A customer makes a slightly larger, slightly unusual transfer → the guard pauses and asks for a one-time password to confirm it's really them → **flagged for verification**.
- Someone tries to drain an entire account at 3 AM in one shot → the guard doesn't wait around → **transaction blocked on the spot**.

**This system is that guard, except it's an AI model instead of a person, and it evaluates every transaction in a fraction of a second.**

It doesn't just watch the dollar amount. It looks at timing, account balances before and after, how much of someone's net worth is moving at once, and whether the numbers even add up correctly — then combines all of that into a single risk score.

---

## 2. Why Old Security Systems Fail

Most traditional bank security runs on simple, hardcoded rules, like:

```
Rule: "If a transfer is greater than $10,000, block it."
```

This sounds reasonable, but it's easy to defeat once you know the rule exists. A fraudster just sends $9,999 four times instead of $40,000 once, and the rule never fires. Rigid rules can only catch what someone already thought to write down in advance.

**Machine learning takes a different approach.** Instead of one rule, the model looks at dozens of subtle signals at the same time, patterns a human wouldn't think to check for, and learns from thousands of real examples what fraud actually tends to look like. It adapts to combinations of behavior, not just a single number crossing a single threshold.

---

## 3. How It Works

Every transaction flows through five stages:

```
[1. Transaction Comes In]
          │
          ▼
[2. Feature Detective]   →  checks timing, balance math, account drain, transfer ratio
          │
          ▼
[3. AI Model]             →  compares against patterns learned from 25,000 past transactions
          │
          ▼
[4. Risk Score + Decision]
          │
          ├── Score < 30%    →  APPROVE  (instant, no friction)
          ├── Score 30–75%   →  FLAG     (ask for OTP / two-factor)
          └── Score > 75%    →  BLOCK    (stopped immediately)
          │
          ▼
[5. Logged to Database + Shown on Live Dashboard]
```

### Step 1 — A transaction arrives
The system receives the basics: transaction type (transfer, cash-out, payment, cash-in, or debit), the amount, the sender's balance before and after, the receiver's balance before and after, and the hour of the day it happened.

### Step 2 — The Feature Detective
Before the AI even sees the data, the system calculates a handful of cybersecurity-flavored red flags:

- **Account draining** — did this transaction empty the sender's balance to exactly zero?
- **Balance math check** — does `old balance − amount` actually equal the new balance? Real fraud attempts often produce balances that don't quite add up.
- **Odd hours** — is this happening between 1 AM and 5 AM, when legitimate activity is rare?
- **Transfer volume ratio** — what percentage of the sender's entire net worth is moving in this one transaction?

### Step 3 — The AI model
The model takes all of the above and estimates the probability that this specific transaction is fraudulent, based on patterns it learned during training.

### Step 4 — The three-tier decision
That probability becomes a risk score from 0–100%, and the score decides what happens: approve, flag for extra verification, or block outright.

### Step 5 — Logging and the dashboard
Every decision, along with the reasoning behind it, is saved to the database and shows up live on the web dashboard.

---

## 4. The Machine Learning, Explained Simply

### What is the model actually doing?
There's no magic here, it's statistical pattern recognition. During training, the model is shown a spreadsheet of **25,000 historical transactions**, each one already labeled:

- **24,500 legitimate** (98%)
- **500 fraudulent** (2%)

That lopsided split is intentional, and it mirrors reality: fraud is genuinely rare compared to normal activity, which is exactly what makes it hard to catch. A lazy model could just guess "legitimate" every single time and still be right 98% of the time, while catching zero fraud. The model is specifically evaluated on how well it finds that rare 2%, not on raw accuracy, which is why recall and F1-score (see below) matter more here than a plain accuracy number would.

### Which models are compared?
Three different algorithms are trained and benchmarked against each other:

1. **Logistic Regression** — a fast, simple linear baseline.
2. **Random Forest** — 100 decision trees voting together on each transaction.
3. **Gradient Boosting** — trees built one after another, each one specifically correcting the mistakes of the last.

Whichever model scores highest on **F1-score and Recall** (i.e., whichever one actually catches the most fraud with the fewest false alarms) is automatically saved and used for live predictions.

---

## 5. Model Results

> Fill this in after running `python run.py` — the training step prints these exact numbers, and `ml/artifacts/` will contain the saved model.

| Model               | Precision | Recall | F1-Score | Notes |
|----------------------|-----------|--------|----------|-------|
| Logistic Regression   | —         | —      | —        | baseline |
| Random Forest         | —         | —      | —        |          |
| Gradient Boosting     | —         | —      | —        |          |

**Winning model:** *(name the one `run.py` selects)*

---

## 6. Web Dashboard

Once the server is running, the dashboard gives you:

- **Transaction Scoring Simulator** — test your own values, or use one-click presets:
  - *Point of Sale*: normal $4.50 coffee payment
  - *Direct Deposit*: legitimate $3,200 salary deposit
  - *High Transfer*: elevated $18,000 business transfer
  - *Account Drain*: suspicious $95,000 wipeout at 3 AM
- **Real-Time Risk Gauge** — a visual bar showing the fraud probability plus a plain-English explanation of why.
- **Multi-Currency Switcher** — toggle between INR (₹), USD ($), EUR (€), and GBP (£) across every form, preset, and table.
- **Analytics Charts** — a live doughnut chart of approved vs. flagged vs. blocked transactions, plus a histogram of how risk scores are distributed.
- **Audit Log Table** — a searchable, filterable log of every transaction the system has evaluated, with timestamps and decisions.

> *(Drop a screenshot or GIF of the dashboard here — it does more to explain this section than any amount of text.)*

---

## 7. Getting Started

### Prerequisites
- Python 3.10, 3.11, or 3.12

### Step 1 — Clone and create a virtual environment

```bash
git clone https://github.com/corvainx/financial-fraud-detection.git
cd financial-fraud-detection
python -m venv venv
```

### Step 2 — Activate the virtual environment

| Shell | Command |
|---|---|
| Linux (bash/zsh) | `source venv/bin/activate` |
| Linux (fish) | `source venv/bin/activate.fish` |
| Windows (PowerShell) | `.\venv\Scripts\Activate.ps1` |
| Windows (cmd) | `venv\Scripts\activate.bat` |

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Run everything

```bash
python run.py
```

This one script handles the whole pipeline:
1. Generates the historical transaction dataset.
2. Trains and benchmarks the three ML models.
3. Saves the winning model to disk.
4. Initializes the database and seeds it with sample history.
5. Starts the web server.

### Step 5 — Open it in your browser

- **Dashboard:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 8. Project Structure

```
fraud_det/
├── data/
│   └── raw/                    # Transaction datasets (auto-generated)
├── ml/
│   ├── dataset_generator.py    # Generates realistic PaySim-style financial data
│   ├── feature_engineering.py  # Extracts the cybersecurity indicators
│   ├── train.py                # Trains and benchmarks the three models
│   ├── evaluate.py             # Computes precision, recall, F1
│   └── artifacts/              # Saved winning model (.joblib)
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI endpoints (/predict, /transactions, /analytics)
│   │   ├── core/                # Config and database connection
│   │   ├── models/              # SQLAlchemy database tables
│   │   ├── schemas/             # Pydantic input/output validation
│   │   └── services/            # Inference engine + 3-tier decision logic
│   └── main.py                  # FastAPI app entry point
├── frontend/
│   ├── index.html               # Dashboard UI
│   ├── css/style.css
│   └── js/app.js                # Simulator, charts, currency switching
├── tests/
│   └── test_pipeline.py
├── requirements.txt
├── run.py                       # One-command bootstrap + launcher
└── README.md
```

---

## 9. Technology Stack

- **Machine Learning:** Python, scikit-learn, pandas, NumPy, joblib
- **Backend API:** FastAPI, Uvicorn, Pydantic
- **Database:** SQLite by default (zero setup), MySQL-compatible via SQLAlchemy
- **Frontend:** HTML5, Tailwind CSS, Chart.js, Lucide Icons