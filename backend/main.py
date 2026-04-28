from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
from fairness_engine import compute_fairness_metrics
from gemini_service import get_bias_explanation

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    return {"columns": list(df.columns), "preview": df.head(3).to_dict(orient="records")}

@app.post("/analyze")
async def analyze_bias(
    file: UploadFile = File(...),
    target: str = Form(...),
    sensitive: str = Form(...)
):
    contents = await file.read()
    try:
        metrics = compute_fairness_metrics(contents, target, sensitive)
        explanation = get_bias_explanation(metrics)
        
        # Determine simple Red/Green status based on Disparate Impact (0.8 - 1.25 is usually acceptable)
        is_biased = metrics["Disparate Impact Ratio"] < 0.8 or metrics["Disparate Impact Ratio"] > 1.25
        
        return {
            "metrics": metrics,
            "explanation": explanation,
            "is_biased": is_biased
        }
    except Exception as e:
        return {"error": str(e)}