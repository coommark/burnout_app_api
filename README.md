# Early Detection of Burnout Risk among IT Professionals Using Lightweight Daily Self-Assessments: A Machine Learning Approach – **Backend API**

**Capstone Project – MSIT 5910**  
**Institution:** University of the People  
**Course:** Master of Science in Information Technology  
**Author:** Mark Yakubu Melton  
**Date:** August 01, 2025

---

## 📍 Project at a Glance

Early Detection of **Burnout Risk among IT Professionals** is the MSIT 5910 capstone project for the University of the People.  
It delivers a _complete, production-style pipeline_—from daily data capture on a phone to real-time ML inference and dashboards—to surface early warning signs of burnout.

---

### 🔄 End-to-End Flow

1. Daily Check-in (Mobile)
2. Secure API Call
3. ML Inference
4. Persistence & Analytics
5. Instant Feedback (Mobile)
6. Offline Retraining Loop

---

### 🧠 Machine-Learning Components

| Item           | Details                                                          |
| -------------- | ---------------------------------------------------------------- |
| Features       | 7-day means of EE, PA, DP (DP = 6 − _meaningfulness_)            |
| Algorithms     | Logistic Regression, Random Forest, **XGBoost**                  |
| Target         | `Low` / `Moderate` / `High` burnout risk + binary _at-risk_ flag |
| Data (Phase 1) | 1 000 simulated users, class-balanced, MBI-aligned               |
| Eval split     | Stratified 70 / 30 hold-out                                      |
| Key metrics    | Per-class P/R/F1, macro ROC-AUC, Brier, log-loss                 |
| Ops target     | **≤ 2 s** p95 API latency (Locust: 61 ms)                        |

---

### 📱 Frontend (React Native / Expo)

- Nine core screens: onboarding, daily assessment, dashboard, profile.
- **Expo Router** navigation & **NativeWind/Tailwind** styling.
- Stores auth state with **JWT** + refresh, handles push-token registration (Expo Notifications).
- Typed API layer via **React Query** hooks with optimistic updates.

### 🔧 Backend (FastAPI / Python 3.10)

- Modular **routers**: `/users`, `/assessments`, `/dashboard`, `/push-token`.
- **Argon2id** password hashing, Pydantic validation, rate-limit & CORS middleware.
- Model inference endpoint hot-loads `.pkl` artefacts; zero-downtime swaps via CI pipeline.
- Structured JSON logging + Prometheus `/metrics` for ops.

---

### 🎯 Research Questions & Objectives

| **RQ / Objective** | **Focus**                                                                                                   |
| ------------------ | ----------------------------------------------------------------------------------------------------------- |
| **RQ1**            | _Accuracy_: Can weekly averages of 3 MBI-aligned items classify Low / Moderate / High burnout?              |
| **RQ2**            | _Model choice_: Which algorithm balances **recall**, **calibration**, and **interpretability** best?        |
| **RQ3**            | _Systems_: Can the prototype deliver **< 1 min** UX + **< 2 s** API inference under ≥ 100 concurrent users? |
| **Primary Goal**   | Prove technical feasibility of low-burden, continuous burnout monitoring on modest infra.                   |
| **Secondary Goal** | Prepare codebase & pipelines for Phase 2: consent-based real-world validation.                              |

---

> **Why it matters:**  
> Intermittent surveys miss day-to-day stress fluctuations.  
> This project shows that a _three-tap daily check-in_ and a _tiny ML service_ are enough for timely, personalised burnout alerts—without intrusive data grabs or heavyweight infrastructure.

---

## Repository Overview

This repository hosts the **FastAPI** backend that powers the capstone’s Early Detection of Burnout mobile app.  
It provides secure REST endpoints for authentication, daily self‑assessment submission, rolling 7‑day analytics, and real‑time machine‑learning risk prediction.

The mobile client lives in a separate repo (see **Mobile‑App** README).

---

## Features

| Category             | Description                                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Auth**             | User registration, login, refresh, and password reset via **JWT** (access + refresh).                         |
| **Daily Assessment** | POST three slider scores (0‑6) — exhaustion, capability, meaningfulness — once per calendar day.              |
| **ML Prediction**    | Submission triggers the latest **XGBoost** pipeline returning _Low / Moderate / High_ risk and probabilities. |
| **Dashboard**        | GET endpoint with 7‑day aggregates & historical predictions for charting.                                     |
| **Push Tokens**      | Register Expo push tokens for daily reminders.                                                                |
| **Audit Logging**    | All critical actions stored in `audit_logs` for traceability.                                                 |

---

## Tech Stack

| Layer         | Technology                        |
| ------------- | --------------------------------- |
| Web Framework | **FastAPI 0.111+**                |
| Language      | **Python 3.10**                   |
| Database      | **PostgreSQL 14**                 |
| ML            | **Scikit‑learn**, **XGBoost**     |
| Auth          | **PyJWT**, **Passlib (Argon2id)** |
| Testing       | **Pytest**, **HTTPX**, **Locust** |
| CI/CD         | **GitHub Actions**                |

---

## Project Structure

```text
backend/
├── app/                 # FastAPI application
│   ├── routers/         # users, assessments, dashboard
│   └── ...
├── model/               # Notebooks & serialized pipelines
├── scripts/             # Utility and migration helpers
├── tests/               # Unit & integration tests
├── locustfile.py        # Load‑test scenarios
├── requirements.txt
└── README.md
```

---

## Setup & Installation

1. **Clone & install**
   ```bash
   git clone <repo-url> && cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Environment**
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/burnout
   SECRET_KEY=change_me
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
3. **Migrations**
   ```bash
   alembic upgrade head
   ```
4. **Run API**
   ```bash
   uvicorn app.main:app --reload
   # Swagger UI → http://localhost:8000/docs
   ```

---

## Testing

```bash
pytest -q               # unit / integration
locust -f locustfile.py # http://localhost:8089
```

Target SLA (local): **p95 ≤ 2 s** for `/assessments/` & `/dashboard/`.

---

## Security

- **TLS 1.3** (terminated by reverse proxy)
- **Argon2id** password hashing
- **JWT** with short‑lived access / long‑lived refresh tokens
- Strict **CORS** & **Rate‑Limiting** middleware
- Server‑side validation with Pydantic

---

## Deployment & Maintenance

| Stage         | Tool / Notes                                      |
| ------------- | ------------------------------------------------- |
| CI            | GitHub Actions – lint → test → build → push image |
| CD            | Docker/K8s/Fly/Render (choose hosting)            |
| Observability | JSON logs + Prometheus metrics (`/metrics`)       |
| Upgrades      | Dependabot PRs, alembic migrations                |

---

## Glossary

| Term           | Meaning                              |
| -------------- | ------------------------------------ |
| **Assessment** | Daily 3‑item survey scored 0‑6       |
| **Prediction** | ML output _Low \| Moderate \| High_  |
| **Rolling 7d** | 7‑day average used as model features |
| **p95**        | 95th‑percentile response time        |
