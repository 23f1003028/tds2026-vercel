from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import os

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load the telemetry data provided in your JSON
# Save your JSON as 'telemetry.json' in the same folder
DATA_PATH = os.path.join(os.path.dirname(__file__), "telemetry.json")

@app.post("/api")
async def get_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)
    
    # Load the JSON file
    df = pd.read_json(DATA_PATH)
    
    response_data = {}
    
    for region in regions:
        region_df = df[df['region'] == region]
        
        if not region_df.empty:
            # Metric Calculations
            avg_lat = region_df['latency_ms'].mean()
            p95_lat = region_df['latency_ms'].quantile(0.95)
            avg_up = region_df['uptime_pct'].mean()
            breach_count = int((region_df['latency_ms'] > threshold).sum())
            
            response_data[region] = {
                "avg_latency": round(float(avg_lat), 2),
                "p95_latency": round(float(p95_lat), 2),
                "avg_uptime": round(float(avg_up), 3),
                "breaches": breach_count
            }
            
    return response_data
