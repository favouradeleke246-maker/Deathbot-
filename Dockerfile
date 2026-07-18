# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies for Chrome and ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    git \
    # Chrome runtime libraries
    libnss3 \
    libx11-6 \
    libgbm1 \
    libxshmfence1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libxfixes3 \
    libcups2 \
    libpango-1.0-0 \
    libatk1.0-0 \
    libdrm2 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome – Method 1: HTTPS repository (preferred)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    || echo "Google Chrome repository failed. Using fallback method."

# Install Chrome – Method 2: Direct .deb download (fallback if repository fails)
RUN if ! command -v google-chrome > /dev/null; then \
        wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
        && apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb \
        && rm google-chrome-stable_current_amd64.deb \
        && rm -rf /var/lib/apt/lists/*; \
    fi

# Install ChromeDriver from Debian repositories (compatible and stable)
RUN apt-get update && apt-get install -y chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Sherlock, Maigret, Holehe globally
RUN pip install --no-cache-dir sherlock-project==0.16.0 maigret==0.6.3 holehe>=0.1.0

# Clone Tookie-OSINT
RUN git clone https://github.com/Alfredredbird/tookie-osint.git /opt/tookie-osint
RUN pip install -r /opt/tookie-osint/requirements.txt || true

# Copy the entire application
COPY . .

# Expose the port
EXPOSE 8080

# Start Gunicorn
CMD ["gunicorn", "webhook_server:app", "--timeout", "300", "--bind", "0.0.0.0:8080"]
