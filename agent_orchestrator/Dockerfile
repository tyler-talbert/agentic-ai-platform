FROM python:3.11-slim

ENV PYTHONPATH=/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

COPY agent_orchestrator/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY agent_orchestrator/ ./agent_orchestrator/
COPY proto/ ./proto/

WORKDIR /app/agent_orchestrator

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
