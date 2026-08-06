FROM python:3.13-slim-bookworm

ENV TZ=Europe/Rome \
    PYTHONUNBUFFERED=1 \
    LOG_FILE=/app/logs/booking_automation.log \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        chromium \
        chromium-driver \
        tzdata && \
    rm -rf /var/lib/apt/lists/* && \
    chromium --version && \
    "$CHROMEDRIVER_PATH" --version

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY src ./src

RUN useradd --create-home bot && \
    mkdir -p /app/logs && \
    chown -R bot:bot /app

USER bot

CMD ["python", "src/main.py"]
