FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install -y curl

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4001"]

