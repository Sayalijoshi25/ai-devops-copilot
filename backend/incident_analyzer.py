from backend.ollama_client import query_ollama


def analyze_incident(log_text: str) -> str:
    prompt = f"""
You are an expert AI DevOps Copilot helping an SRE investigate production issues.

Analyze the following log and return the response in this exact format:

Incident Summary:
<short summary>

Possible Root Cause:
<likely cause>

Severity:
<low/medium/high/critical>

Immediate Actions:
- action 1
- action 2
- action 3

Suggested Commands to Verify:
- command 1
- command 2
- command 3

Log:
{log_text}
"""
    return query_ollama(prompt)
