FROM python:3.10-slim

WORKDIR /app

# Install git for cloning repos
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install dependencies (adjust as needed)
RUN pip install --no-cache-dir gitpython openai

# Copy agent code
COPY agent.py .

CMD ["python", "agent.py"]

