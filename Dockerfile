FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
# Required for Xvfb virtual display
ENV DISPLAY=:99

# Install Chromium, chromedriver, Xvfb, and required libraries
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxkbcommon0 \
    libxdamage1 \
    libgbm1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libxcomposite1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Start Xvfb and then run your Selenium script
CMD ["sh", "-c", "Xvfb :99 & sleep 5 && python3 -m app.main"]
