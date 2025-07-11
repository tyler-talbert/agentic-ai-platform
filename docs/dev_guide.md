# 🛠️ Developer Guide — Agentic AI Platform

## 1 · Prerequisites

| Tool | Version (min) |
|------|---------------|
| Docker | 24.x |
| Docker Compose | v2 plugin |
| Make | optional (for shortcuts) |

First-run download size ≈ 8 GB (Ollama + models).

---

## 2 · Environment Variables

Create a `.env` file in the repo root:

~~~env
# gRPC
AGENT_GRPC_URL=agent_service:50051      # Docker default (host: agent_service)
# For host-only testing, export: AGENT_GRPC_URL=localhost:50051

# LLM & Embeddings
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_EMBEDDING_URL=http://ollama:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_EMBEDDING_DIM=768
LLM_TEMPERATURE=0.1

# Pinecone
PINECONE_API_KEY=<your-key>
PINECONE_ENV=gcp-starter
PINECONE_INDEX_NAME=agent-knowledge-base
PINECONE_INDEX_DIM=768
PINECONE_INDEX_METRIC=cosine

# Kafka
KAFKA_BROKER=kafka:9092
TOPIC_IN=agent-tasks-inbound
TOPIC_OUT=agent-tasks-completed
~~~

A sample file lives at `docs/dev.env.example`.

---

## 3 · Running the Stack

~~~bash
docker compose up --build        # full rebuild
docker compose up                # subsequent runs
~~~

*Orchestrator:* <http://localhost:4000>  
*Agent debug endpoint:* <http://localhost:4001>  
*gRPC health check:* `grpc-health-check -addr localhost:50051`

---

## 4 · Tests & CI

Local run:

~~~bash
make test      # unit + integration + e2e
~~~

CI replicates this inside GitHub Actions, spinning Kafka, Ollama, and both services.

---

## 5 · Common Tasks

| Task | Command |
|------|---------|
| Lint & format           | `make lint` |
| Rebuild orchestrator    | `docker compose build agent_orchestrator` |
| Pull a new Ollama model | `docker exec -it ollama ollama pull mistral` |
| Tear down everything    | `docker compose down -v` |

---

## 6 · Debugging Tips

* Add `provector/kafka-ui` to `docker-compose.yml` for a Kafka topic viewer.  
* Use the Pinecone dashboard → **Vectors** tab to verify upserts.  
* Set `LOG_LEVEL=DEBUG` before `docker compose up` for verbose logs.
