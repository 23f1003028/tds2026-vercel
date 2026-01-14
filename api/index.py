from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# Robust CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],           # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],           # Allows all headers
    expose_headers=["*"]
)

# Use absolute path for the JSON file to ensure Vercel finds it
DATA_PATH = os.path.join(os.path.dirname(__file__), "telemetry.json")

@app.post("/api")
async def get_metrics(request: Request):
    try:
        body = await request.json()
        regions = body.get("regions", [])
        threshold = body.get("threshold_ms", 180)
        
        # Load the JSON
        df = pd.read_json(DATA_PATH)
        
        response_data = {}
        for region in regions:
            region_df = df[df['region'] == region]
            
            if not region_df.empty:
                avg_lat = region_df['latency_ms'].mean()
                p95_lat = region_df['latency_ms'].quantile(0.95)
                avg_up = region_df['uptime_pct'].mean()
                breaches = int((region_df['latency_ms'] > threshold).sum())
                
                response_data[region] = {
                    "avg_latency": float(avg_lat),
                    "p95_latency": float(p95_lat),
                    "avg_uptime": float(avg_up),
                    "breaches": breaches
                }
                
        return response_data
    except Exception as e:
        return {"error": str(e)}
