# SLA Breach Prediction — ML-Powered IT Service Management

> **Predict SLA breaches before they happen.** An end-to-end machine learning pipeline that scores every Jira ticket in real time, triggers automated escalations for high-risk tickets, and supports voice-based ticket creation — all deployed in the cloud with no local installation required.

---

## 🔗 Live Links

| Service | URL |
|---|---|
| **Model API** | [sla-model-api-1.onrender.com/docs](https://sla-model-api-1.onrender.com/docs) |
| **SLA ROI Calculator** | [sla-roi-calculator.onrender.com](https://sla-roi-calculator.onrender.com) |
| **Architecture & Workflows** | [Workflow_architecture.html](./Workflow_architecture.html) |

---

## 📋 What This Does

ServiceNow's internal IT service desk manages thousands of support tickets daily. SLA breaches — where a ticket is not resolved within the agreed time — carry financial penalties and reputational damage. The problem is that breaches are only discovered **after they occur**, leaving no time for corrective action.

This project builds a complete automated pipeline that:

1. **Predicts** the probability of SLA breach at ticket creation and on every update
2. **Scores** every Jira ticket automatically via a REST API
3. **Escalates** high-risk tickets by adding labels, posting comments, and sending email alerts — without any agent action
4. **Supports voice entry** — callers dial a phone number, speak their issue, and a Jira ticket is created and scored automatically

---

## 📁 Repository Structure

```
sla-model-api/
│
├── ml_pipeline/
│   ├── Predict_SLA_breach_probability.ipynb   # Full ML pipeline (EDA → model → evaluation)
│   ├── Fast_API_code.ipynb                    # FastAPI deployment notebook
│   ├── main.py                                # FastAPI application (deployed on Render)
│   ├── requirements.txt                       # Python dependencies
│   └── sla_breach_model.pkl                   # Trained XGBoost model + preprocessor
│
├── workflows/
│   └── Workflow_architecture.html             # Architecture & workflow diagrams
│
├── calculator/
│   └── index.html                             # Interactive SLA ROI calculator (static site)
│
└── README.md
```

> **Render deployment note:** the model API Root Directory is set to `ml_pipeline/` in Render settings so `main.py` is found correctly.

---

## 🤖 Machine Learning Model

**Dataset:** [UCI — Incident Management Process Enriched Event Log](https://archive.ics.uci.edu/dataset/498/incident+management+process+enriched+event+log)
- 141,712 events across 24,918 unique tickets
- Binary classification target: `sla_breached` (1 = breach, 0 = met SLA)
- Class split: 63.4% met SLA / 36.6% breached

**Algorithm:** XGBoost (gradient boosted trees)

**Key results at threshold 0.45:**

| Metric | Baseline (Logistic Regression) | XGBoost |
|---|---|---|
| Recall (breach class) | 0.67 | **0.84** |
| Precision | 0.60 | 0.57 |
| F1-Score | 0.64 | 0.68 |
| AUC-ROC | 0.794 | **0.817** |

**Top SHAP features:** `hours_open_to_update`, `knowledge`, `assignment_group_Group 70`, `open_hour`, `priority`

---

## 🚀 API Reference

**Base URL:** `https://sla-model-api-1.onrender.com`

**Interactive docs:** [`/docs`](https://sla-model-api-1.onrender.com/docs)

### POST `/predict`

Scores a single ticket and returns the breach probability and risk level.

**Headers:**
```
Content-Type: application/json
X-API-Key: your-api-key
```

**Request body:**
```json
{
  "impact": "2 - Medium",
  "urgency": "2 - Medium",
  "priority": "3 - Moderate",
  "contact_type": "Email",
  "category": "Category 51",
  "assignment_group": "Group 70",
  "knowledge": false,
  "reassignment_count": 0,
  "reopen_count": 0,
  "sys_mod_count": 0,
  "hours_open_to_update": 2.5,
  "open_hour": 9,
  "open_dayofweek": 1,
  "is_weekend": 0
}
```

**Response:**
```json
{
  "breach_probability": 0.73,
  "breach_predicted": true,
  "risk_level": "HIGH"
}
```

**Risk levels:** `LOW` (< 0.35) · `MEDIUM` (0.35–0.45) · `HIGH` (> 0.45)

> **Note:** Category and assignment group values must match the dataset naming convention (e.g. `Category 51`, `Group 70`) for the one-hot encoding to align correctly with the trained model.

---

## ⚙️ Automation Workflows

### 1 · Jira SLA Breach Scoring (n8n)

Triggered on every Jira ticket event. Seven nodes:

```
Jira Trigger → Code node → HTTP Request (/predict) → IF (risk == HIGH)
    ├── TRUE → Jira REST API (add label) → Jira comment → Send email
    └── FALSE → Stop (no action)
```

### 2 · Voice Ticket Creation (ElevenLabs + Twilio + n8n)

```
Caller ↔ Twilio ↔ ElevenLabs AI Agent → n8n Webhook → Jira create issue
                                                              ↓
                                              SLA scoring workflow triggered
```

See [`Workflow_architecture.html`](./Workflow_architecture.html) for full visual diagrams.

---

## 📊 SLA ROI Calculator

An interactive web calculator that estimates the financial impact of the prediction system based on your organisation's ticket volume, penalty per breach, model recall, and agent action rate.

**Live:** [sla-roi-calculator.onrender.com](https://sla-roi-calculator.onrender.com)

Source: [`calculator/index.html`](./calculator/index.html)

---

## 🛠️ Local Setup

```bash
# Clone the repository
git clone https://github.com/Pokam-Abukakar/sla-model-api.git
cd sla-model-api

# Install dependencies
pip install -r requirements.txt

# Run the API locally
uvicorn main:app --reload
```

API will be available at `http://localhost:8000/docs`

---

## 🏗️ Deployment

| Component | Platform | Type |
|---|---|---|
| Model API (`main.py`) | Render | Web Service |
| ROI Calculator (`calculator/`) | Render | Static Site |
| Automation workflows | n8n Cloud | Workflow |
| Voice agent | ElevenLabs + Twilio | Conversational AI |
| Ticketing | Jira Service Management | Cloud |

---

## 📚 Academic Context

This project was developed as part of an **Artificial Intelligence** module case study, implementing a full ML pipeline from data exploration through to production deployment. The case study is based on ServiceNow's internal IT service desk context using the UCI incident management dataset.


> AI usage: Claude (Anthropic, 2026) was used as an AI assistant for code debugging, document structuring, and text formulation. All technical decisions, model selection, threshold choices, and architectural design were made by the author.

---

## 📄 References

- Seredov et al. (2018). *Incident Management Process Enriched Event Log*. UCI ML Repository. [Link](https://archive.ics.uci.edu/dataset/498/incident+management+process+enriched+event+log)
- Chen & Guestrin (2016). *XGBoost: A scalable tree boosting system*. KDD 2016.
- Grinsztajn et al. (2022). *Why tree-based models still outperform deep learning on tabular data*. NeurIPS 2022.
- Lundberg & Lee (2017). *A unified approach to interpreting model predictions*. NeurIPS 2017.
