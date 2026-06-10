FROM python:3.12-slim AS base

ENV NODE_MAJOR=22
ENV PLAYWRIGHT_VERSION=1.59.1

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies (layer cached independently)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package files first for npm layer caching
COPY package.json package-lock.json* ./
RUN npm ci && \
    npx playwright install --with-deps chromium

# Copy application code
COPY . .

EXPOSE 3000

ENTRYPOINT ["python", "orchestrator.py"]
CMD ["--help"]
