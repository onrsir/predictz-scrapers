FROM python:3.11-slim

# Node.js kurulumu
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Node.js dependencies
WORKDIR /app/Predictor
RUN npm install

# Ana dizine dön
WORKDIR /app

# Port expose et (health check için)
EXPOSE 8080

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Istanbul

# Automation scheduler'ı başlat
CMD ["python", "automation/automation_scheduler.py"]
