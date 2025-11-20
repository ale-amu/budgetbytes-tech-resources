# Use lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Avoid Python buffering in logs
ENV PYTHONUNBUFFERED=1

# Install system dependencies required by Azure SDK
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the Flask port
EXPOSE 8080

# Start the app
CMD ["python3", "app.py"]
