FROM python:3.13.2-slim-bookworm AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13.2-slim-bookworm

WORKDIR /app 

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc bubblewrap libc6-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY build build
COPY . .

RUN useradd -m appuser && chown -R appuser /app

USER appuser

ENTRYPOINT [ "python", "build/build.py" ]
