FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd --system appgroup \
    && useradd --system --gid appgroup --create-home appuser

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8080

WORKDIR /app/src
CMD ["python", "app.py"]
