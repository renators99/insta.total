# Use the official Python image as a base
FROM --platform=linux/amd64 python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=True

# Install OS dependencies and Google Chrome
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    jq \
    unzip \
    wget \
    apt-transport-https \
    ca-certificates \
    gnupg \
    --no-install-recommends \
 && rm -rf /var/lib/apt/lists/* \
 && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
 && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
 && apt-get update \
 && apt-get install -y google-chrome-stable \
 && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
 && wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip -O /tmp/chromedriver.zip \
 && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ \
 && rm /tmp/chromedriver.zip

WORKDIR /app

# Install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Expose the default port
EXPOSE 80

# Set the entrypoint
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]