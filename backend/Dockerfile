# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies needed for compiling certain Python packages
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to take advantage of Docker caching layers
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Start Uvicorn (Adjust 'app.main:app' if your entry point file is named differently)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
