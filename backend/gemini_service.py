import requests
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

def get_bias_explanation(metrics: dict) -> str:
    prompt = f"""
    You are an AI fairness expert. Analyze these machine learning fairness metrics:
    {metrics}

    1. Explain whether this model is biased in plain English.
    2. Suggest 3 practical mitigation strategies.

    Keep the response concise, formatted in Markdown, and easy to understand for non-technical stakeholders.
    """

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }

    try:
        response = requests.post(GEMINI_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
        return "Unable to extract explanation from response."
    except Exception as e:
        return f"Error connecting to Gemini API: {str(e)}"
