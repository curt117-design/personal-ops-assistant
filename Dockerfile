FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY .env* ./

# Set working directory to src for imports
WORKDIR /app/src

# Create logs directory
RUN mkdir -p /app/logs

CMD ["python", "main.py"]
