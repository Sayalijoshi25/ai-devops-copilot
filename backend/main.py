#testing commit
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import subprocess
import requests
from openai import OpenAI

from backend.metrics_collector import collect_metrics
from backend.incident_analyzer import analyze_incident


# ----------------------------
# Slack Alert Function
# ----------------------------
def send_slack_alert(message: str):
    webhook = os.getenv("SLACK_WEBHOOK_URL")

    if webhook:
        try:
            requests.post(webhook, json={"text": message}, timeout=10)
        except Exception as e:
            print("Slack alert failed:", e)


# ----------------------------
# Logging Setup
# ----------------------------
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ----------------------------
# OpenAI Client
# ----------------------------
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key) if openai_api_key else None


# ----------------------------
# FastAPI App
# ----------------------------
app = FastAPI()


# ----------------------------
# CORS Middleware
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Helper: OpenAI Log Analysis
# ----------------------------
def analyze_with_openai(logs: str, include_metrics: bool = False) -> str:
    if not client:
        raise ValueError("OPENAI_API_KEY is not set.")

    metrics_text = ""
    if include_metrics:
        metrics = collect_metrics()
        metrics_text = f"""
System metrics at time of incident:

CPU Usage: {metrics.get('cpu_percent')}%
Memory Usage: {metrics.get('memory_percent')}%
Disk Usage: {metrics.get('disk_percent')}%
System Load: {metrics.get('load_avg')}
"""

    prompt = f"""
You are a senior DevOps engineer.

{metrics_text}

Analyze the following logs and provide:

1. Issue
2. Root cause
3. Suggested fix
4. Severity

Logs:
{logs}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are an expert DevOps troubleshooting assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# ----------------------------
# Root Endpoint
# ----------------------------
@app.get("/")
def read_root():
    logging.info("Root endpoint accessed")
    return {"message": "AI DevOps Copilot Backend Running"}


@app.get("/favicon.ico")
async def favicon():
    return {"status": "ok"}


# ----------------------------
# Generate Sample Error
# ----------------------------
@app.get("/error")
def generate_error():
    try:
        x = 1 / 0
        return {"result": x}
    except Exception as e:
        logging.error(f"Application error: {e}")
        return {"error": "Something went wrong"}


# ----------------------------
# Analyze Local Logs with OpenAI
# ----------------------------
@app.get("/analyze-logs")
def analyze_logs():
    try:
        with open("logs/app.log", "r") as f:
            logs = f.read()[-4000:]

        analysis = analyze_with_openai(logs, include_metrics=True)

        send_slack_alert(f"""
🚨 AI DevOps Incident

{analysis}
""")

        return {"analysis": analysis}

    except Exception as e:
        return {"error": str(e)}


# ----------------------------
# Analyze Local Logs with Ollama
# ----------------------------
@app.get("/analyze-logs-ollama")
def analyze_logs_ollama():
    try:
        with open("logs/app.log", "r") as f:
            logs = f.read()[-4000:]

        analysis = analyze_incident(logs)

        send_slack_alert(f"""
🚨 AI DevOps Incident (Ollama)

{analysis}
""")

        return {"analysis": analysis}

    except Exception as e:
        return {"error": str(e)}


# ----------------------------
# Analyze Raw Log Text with Ollama
# ----------------------------
@app.post("/analyze")
def analyze_text(logs: str = Query(..., description="Raw log text to analyze")):
    try:
        analysis = analyze_incident(logs)
        return {"analysis": analysis}
    except Exception as e:
        return {"error": str(e)}


# ----------------------------
# Upload Log File
# ----------------------------
@app.post("/upload-log")
async def upload_log(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        logs = contents.decode("utf-8")

        analysis = analyze_with_openai(logs, include_metrics=True)

        send_slack_alert(f"""
🚨 AI DevOps Incident

{analysis}
""")

        return {"analysis": analysis}

    except Exception as e:
        return {"error": str(e)}


# ----------------------------
# Upload Log File with Ollama
# ----------------------------
@app.post("/upload-log-ollama")
async def upload_log_ollama(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        logs = contents.decode("utf-8")

        analysis = analyze_incident(logs)

        send_slack_alert(f"""
🚨 AI DevOps Incident (Ollama)

{analysis}
""")

        return {"analysis": analysis}

    except Exception as e:
        return {"error": str(e)}


# ----------------------------
# Analyze Container Logs with OpenAI
# ----------------------------
@app.get("/analyze-container")
def analyze_container(container: str):
    try:
        logs = subprocess.check_output(
            ["docker", "logs", container],
            stderr=subprocess.STDOUT
        ).decode()

        analysis = analyze_with_openai(logs, include_metrics=True)

        send_slack_alert(f"""
🚨 Container Incident Detected

Container: {container}

{analysis}
""")

        return {"analysis": analysis}

    except Exception as e:
        return {"error": str(e)}


# ----------------------------
# Analyze Container Logs with Ollama
# ----------------------------
@app.get("/analyze-container-ollama")
def analyze_container_ollama(container: str):
    try:
        logs = subprocess.check_output(
            ["docker", "logs", container],
            stderr=subprocess.STDOUT
        ).decode()

        analysis = analyze_incident(logs)

        send_slack_alert(f"""
🚨 Container Incident Detected (Ollama)

Container: {container}

{analysis}
""")

        return {"analysis": analysis}

    except Exception as e:
        return {"error": str(e)}


# ----------------------------
# Metrics Endpoint
# ----------------------------
@app.get("/metrics")
def get_metrics():
    metrics = collect_metrics()
    return metrics
