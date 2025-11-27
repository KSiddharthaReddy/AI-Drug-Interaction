import sys
import os

# Make sure Python can see the ../ml folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "ml"))
if ML_PATH not in sys.path:
    sys.path.append(ML_PATH)

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from risk_scoring import compute_regimen_risk
from recommendation_engine import recommend_alternatives
import pandas as pd

app = FastAPI(title="AI Drug Interaction & Safety API")

# CORS for dashboard + mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data for visualization
drugs_df = pd.read_csv("../data_processed/kg_drugs.csv")
interactions_df = pd.read_csv("../data_processed/kg_interactions.csv")

class RiskRequest(BaseModel):
    drug_ids: List[str]
    age: int | None = None
    sex: str | None = None

class RecommendRequest(BaseModel):
    drug_ids: List[str]
    target_drug: str

@app.get("/")
def root():
    return {"message": "API is running"}

@app.post("/risk_score")
def risk_score(request: RiskRequest):
    result = compute_regimen_risk(request.drug_ids, age=request.age, sex=request.sex)
    return {"risk": result}

@app.post("/recommend_drug")
def recommend(request: RecommendRequest):
    recs = recommend_alternatives(request.drug_ids, request.target_drug)
    return {"recommendations": recs}

@app.get("/interaction_graph")
def interaction_graph():
    nodes = [{"id": row["drug_id"], "label": row["name"]} for _, row in drugs_df.iterrows()]
    edges = [{"source": row["drug1_id"], "target": row["drug2_id"]} for _, row in interactions_df.iterrows()]
    return {"nodes": nodes, "edges": edges}
