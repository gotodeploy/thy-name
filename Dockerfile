FROM ghcr.io/astral-sh/uv:0.2.33 as uv
FROM python:3.12.4-slim-bullseye

RUN --mount=from=uv,source=/uv,target=./uv \
    ./uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app/
COPY . /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=from=uv,source=/uv,target=./uv \
    ./uv pip install  -r requirements.txt

ENTRYPOINT [ "python", "./src/main.py" ]