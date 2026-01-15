from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "telemetry.json")

with open(JSON_PATH, "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)

@app.post("/api/metrics")
async def get_metrics(payload: dict = Body(...)):
    target_regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)
    
    results = {}

    for region in target_regions:
        # Filter for the specific region
        region_df = df[df['region'] == region]
        
        if region_df.empty:
            continue
            
        # Perform calculations
        # Using .tolist() or float() ensures the data is JSON-serializable
        latencies = region_df['latency_ms']
        uptimes = region_df['uptime_pct'] # Note: key is uptime_pct in your JSON

        results[region] = {
            "avg_latency": round(float(latencies.mean()), 2),
            "p95_latency": round(float(latencies.quantile(0.95)), 2),
            "avg_uptime": round(float(uptimes.mean()), 2),
            "breaches": int((latencies > threshold).sum())
        }

    return results
