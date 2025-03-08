# Use the official Python 3.11 image
FROM python:3.11-slim-buster

# Set a working directory within the container
WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

WORKDIR /app/src
