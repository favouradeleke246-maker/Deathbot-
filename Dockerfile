FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install all Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Force install google-generativeai (bypass any dependency resolution issues)
RUN pip install --no-cache-dir google-generativeai==0.5.0

# Copy the entire application code
COPY . .

# Expose the port (Railway uses $PORT, but we set 8080 as default)
EXPOSE 8080

# Start Gunicorn with the correct entry point
CMD ["gunicorn", "webhook_server:app", "--timeout", "300", "--bind", "0.0.0.0:8080"]
