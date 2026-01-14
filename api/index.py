from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import json

app = FastAPI()

# 1. Standard FastAPI CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use absolute path for the JSON file to ensure Vercel finds it
DATA_PATH = os.path.join(os.path.dirname(__file__), "telemetry.json")

@app.post("/api")
async def get_metrics(request: Request):
    # Set headers manually to be absolutely sure they are included
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }

    try:
        body = await request.json()
        regions_list = body.get("regions", [])
        threshold = body.get("threshold_ms", 180)

        # Load data
        df = pd.read_json(DATA_PATH)
        
        region_metrics = {}
        for region in regions_list:
            region_df = df[df['region'] == region]
            
            if not region_df.empty:
                avg_lat = region_df['latency_ms'].mean()
                p95_lat = region_df['latency_ms'].quantile(0.95)
                avg_up = region_df['uptime_pct'].mean()
                breaches = int((region_df['latency_ms'] > threshold).sum())
                
                region_metrics[region] = {
                    "avg_latency": float(avg_lat),
                    "p95_latency": float(p95_lat),
                    "avg_uptime": float(avg_up),
                    "breaches": breaches
                }
        
        # Combine into the required "regions" structure
        result = {"regions": region_metrics}
        
        return Response(content=json.dumps(result), headers=headers, media_type="application/json")

    except Exception as e:
        return Response(content=json.dumps({"error": str(e)}), status_code=400, headers=headers)

# 2. Handle Preflight OPTIONS requests explicitly if middleware fails
@app.options("/api")
async def preflight():
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    return Response(content="OK", headers=headers)
