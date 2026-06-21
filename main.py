
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import joblib, pandas as pd, os

artefacts = joblib.load("sla_breach_model.pkl")
model, scaler = artefacts["model"], artefacts["scaler"]
feature_names, threshold = artefacts["feature_names"], artefacts["threshold"]
API_KEY = os.environ.get("MODEL_API_KEY", "change-this-secret-key")

app = FastAPI()

class TicketInput(BaseModel):
    impact: str
    urgency: str
    priority: str
    contact_type: str
    category: str
    knowledge: bool = False
    reassignment_count: int = 0
    reopen_count: int = 0
    sys_mod_count: int = 0
    assignment_group: str
    hours_open_to_update: float = 0
    open_hour: int
    open_dayofweek: int
    is_weekend: int

def check_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Wrong API key")

@app.get("/health")
def health():
    return {"status": "running"}

@app.post("/predict")
def predict(ticket: TicketInput, authorized: str = Depends(check_key)):
    row = pd.DataFrame([ticket.dict()])
    ordinal_map = {"1 - Critical":4,"2 - High":3,"3 - Moderate":2,"4 - Low":1}
    for col in ["priority","impact","urgency"]:
        row[col] = row[col].map(ordinal_map).fillna(0)
    row_encoded = pd.get_dummies(row).reindex(columns=feature_names, fill_value=0)
    row_scaled = scaler.transform(row_encoded)
    prob = float(model.predict_proba(row_scaled)[0, 1])
    return {
        "breach_probability": round(prob, 4),
        "breach_predicted": prob >= threshold,
        "risk_level": "HIGH" if prob >= 0.7 else "MEDIUM" if prob >= threshold else "LOW"
    }
