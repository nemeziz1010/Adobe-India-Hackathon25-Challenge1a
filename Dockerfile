# Stage 1: The Builder
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Pin the poetry version for a more reliable build
RUN pip install "poetry>=1.5.0" && \
    poetry self add poetry-plugin-export


# Optional: Ensure poetry is available in PATH
RUN ln -s /usr/local/bin/poetry /usr/bin/poetry

WORKDIR /build

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

RUN pip wheel -r requirements.txt --wheel-dir /wheels

# Stage 2: Final Image
FROM python:3.12-slim

COPY --from=builder /wheels /wheels

RUN pip install --no-cache-dir /wheels/*

WORKDIR /app

# Copy the whole app folder into the container’s /app/app
COPY ./app ./app

CMD ["python", "-m", "app.main"]
