FROM python:3.13.2-slim-bookworm AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13.2-slim-bookworm

WORKDIR /app 

COPY --from=builder /install /usr/local
COPY build build

RUN useradd -m appuser && chown -R appuser /app

USER appuser

ENTRYPOINT [ "python", "build/build.py" ]
