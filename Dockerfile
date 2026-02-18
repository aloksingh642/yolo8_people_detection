# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download YOLO weights automatically (cleaner than committing them)
RUN wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O /app/yolov8n.pt

# Copy project files
COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]