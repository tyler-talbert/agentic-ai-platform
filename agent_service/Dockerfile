FROM python:3.11-slim

ENV PYTHONPATH=/app:/app/proto

WORKDIR /app

COPY agent_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install -y curl

COPY agent_service/ ./agent_service/
COPY proto/ ./proto/

WORKDIR /app/agent_service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4001"]

