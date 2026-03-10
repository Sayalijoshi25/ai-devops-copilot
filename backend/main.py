
from fastapi import FastAPI
import logging
import os
from openai import OpenAI
from fastapi import UploadFile, File
import subprocess

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

@app.get("/")
def read_root():
    logging.info("Root endpoint accessed")
    return {"message": "AI DevOps Copilot Backend Running"}

@app.get("/favicon.ico")
async def favicon():
    return {"status": "ok"}


@app.get("/error")
def generate_error():
    try:
        x = 1 / 0
    except Exception as e:
        logging.error(f"Application error: {e}")
        return {"error": "Something went wrong"}

@app.get("/analyze-logs")
def analyze_logs():

    try:
        with open("logs/system.log", "r") as f:
            logs = f.read()[-4000:]

        prompt = f"""
Analyze these DevOps system logs and provide:

1. Issue
2. Root cause
3. Suggested fix

Logs:
{logs}
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a DevOps troubleshooting expert."},
                {"role": "user", "content": prompt}
            ]
        )

        return {"analysis": response.choices[0].message.content.replace("\\n", "\n")}

    except Exception as e:
        return {"error": str(e)}

@app.post("/upload-log")
async def upload_log(file: UploadFile = File(...)):

    contents = await file.read()
    logs = contents.decode("utf-8")

    prompt = f"""
You are a senior DevOps engineer.

Analyze these logs and provide:

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
            {"role": "system", "content": "You are a DevOps troubleshooting expert."},
            {"role": "user", "content": prompt}
        ]
    )

    return {"analysis": response.choices[0].message.content}

@app.get("/analyze-container")
def analyze_container(container: str):

    try:
        logs = subprocess.check_output(
            ["docker", "logs", container],
            stderr=subprocess.STDOUT
        ).decode()

        prompt = f"""
You are a senior DevOps engineer.

Analyze the following container logs and provide:

1. Issue
2. Root Cause
3. Suggested Fix
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

        return {"analysis": response.choices[0].message.content}

    except Exception as e:
        return {"error": str(e)}


