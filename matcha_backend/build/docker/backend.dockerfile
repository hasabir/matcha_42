FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    # postgresql-dev \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


COPY build/docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python3", "app.py"]


