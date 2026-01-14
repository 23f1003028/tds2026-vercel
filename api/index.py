from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# Robust CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Use absolute path for the JSON file
DATA_PATH = os.path.join(os.path.dirname(__file__), "telemetry.json")

@app.post("/api")
async def get_metrics(request: Request):
    try:
        body = await request.json()
        regions_requested = body.get("regions", [])
        threshold = body.get("threshold_ms", 180)
        
        # Load the JSON
        df = pd.read_json(DATA_PATH)
        
        # This is the dictionary that will hold our metrics
        region_metrics = {}
        
        for region in regions_requested:
            region_df = df[df['region'] == region]
            
            if not region_df.empty:
                # Calculate metrics
                avg_lat = region_df['latency_ms'].mean()
                p95_lat = region_df['latency_ms'].quantile(0.95)
                avg_up = region_df['uptime_pct'].mean()
                breach_count = (region_df['latency_ms'] > threshold).sum()
                
                # Assign to the dictionary
                region_metrics[region] = {
                    "avg_latency": float(avg_lat),
                    "p95_latency": float(p95_lat),
                    "avg_uptime": float(avg_up),
                    "breaches": int(breach_count)
                }
        
        # WRAP the result in a "regions" key
        return {"regions": region_metrics}
        
    except Exception as e:
        return {"error": str(e)}
