import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "llama3",
    "prompt": "You are a DevOps assistant. Analyze this log: ERROR disk latency high on node 3",
    "stream": False
}

response = requests.post(url, json=payload, timeout=120)
response.raise_for_status()

data = response.json()
print("\nOllama response:\n")
print(data["response"])
