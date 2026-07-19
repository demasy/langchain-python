# The app image: a small Python runtime with our LangChain agent inside.
FROM python:3.12-slim

WORKDIR /app

# tzdata lets the current_time tool resolve named timezones (e.g. Africa/Cairo).
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first so Docker can cache this layer between code edits.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent source.
COPY main.py .

# Start the interactive agent when the container runs.
CMD ["python", "main.py"]
