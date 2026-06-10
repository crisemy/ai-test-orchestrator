FROM python:3.12-slim AS base

ENV NODE_MAJOR=22
ENV PLAYWRIGHT_VERSION=1.59.1

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers (chromium only for smaller size)
RUN npm init -y && \
    npm install @playwright/test@^${PLAYWRIGHT_VERSION} http-server@^14.1.1 && \
    npx playwright install --with-deps chromium

# Copy application code
COPY . .

# Install TypeScript for tsc validation gate
RUN npm install typescript

# Expose ui-testing-lab port
EXPOSE 3000

# Default: show help
CMD ["--help"]
