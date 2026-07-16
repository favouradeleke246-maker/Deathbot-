FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Force install google-generativeai (bypass any dependency issues)
RUN pip install --no-cache-dir google-generativeai==0.5.0

COPY . .

EXPOSE 8080

CMD ["gunicorn", "webhook_server:app", "--timeout", "300", "--bind", "0.0.0.0:8080"]
