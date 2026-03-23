FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    tcpdump \
    net-tools \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p src/storage/logs

EXPOSE 5000

ENV PYTHONPATH=/app

CMD ["python", "src/main.py"]