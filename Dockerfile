FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
