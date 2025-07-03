[![Maintenance](https://img.shields.io/badge/maintained-yes-brightgreen.svg)](https://github.com/tyler-talbert/agentic-ai-platform)

# 🧠 Agentic AI Platform — Real-Time RAG & Orchestration Spike

Two Docker-compose services that showcase **Retrieval-Augmented Generation (RAG)** with local LLMs, Pinecone vector search, a 768 → 256 auto-encoder for compressed embeddings, and Kafka-based task orchestration.  
Built as an interview-ready spike to demonstrate FAANG-calibre architectural thinking.

---

## 🚀 Quick Start

~~~bash
git clone https://github.com/tyler-talbert/agentic-ai-platform.git
cd agentic-ai-platform
docker compose up                    # orchestrator, agent, Kafka, Zookeeper, Ollama
~~~

1. **Create a task**

~~~bash
curl -X POST http://localhost:4000/v1/tasks \
     -H "Content-Type: application/json" \
     -d '{"input": "Who won the 2024 NBA Finals?"}'
~~~

2. **Poll task status**

~~~bash
curl http://localhost:4000/v1/tasks/<TASK_ID>
~~~

---

## ⚡ gRPC Quick-Start

~~~bash
grpcurl -plaintext \
  -d '{"task_id":"demo","payload":"ping"}' \
  localhost:50051 agent.AgentService/RunTask
~~~

If the command fails with `server does not support the reflection API`, rebuild
the Docker images so the `grpcio-reflection` dependency is installed:

~~~bash
docker compose up --build
~~~

For Windows **cmd.exe**, run the command on a single line and escape the JSON quotes:

~~~cmd
.\grpcurl.exe -plaintext -d '{\"task_id\":\"123\",\"payload\":\"ping\"}' localhost:50051 agent.AgentService/RunTask
~~~

Expect a `COMPLETED` reply with the LLM output.

---

## 🧙‍♂️ Auto-Encoder Runtime Flags

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTOENCODER_WEIGHTS` | `autoencoder.pt` | PyTorch weights loaded by the agent for 256-dim encoding |
| `PINECONE_COMPRESSED_INDEX` | `agent-knowledge-base-256` | 256-dim Pinecone index used for compressed vectors |
| `RELEVANCE_THRESHOLD` | `0.75` | Similarity cutoff after retrieval |

Train your own weights:

~~~bash
python -m agent_service.app.pytorch.train_autoencoder \
       --sample-size 5000 --epochs 3
~~~

Then back-fill the compressed index with `backfill_encoded_vectors.py`.

---

## 🏗️ Architecture Snapshot

| Component            | Host Port(s)          | Purpose |
|----------------------|-----------------------|---------|
| **agent_orchestrator** | **4000**            | REST API (`/v1/tasks`, `/health`, `/run-agent`); embeds prompt, upserts to Pinecone; publishes Kafka messages; issues synchronous gRPC calls |
| **agent_service**      | **4001**, **50051** | FastAPI debug endpoint (4001); gRPC server (50051); consumes tasks, runs RAG, publishes results |
| **Kafka**              | 9092                | Topics `agent-tasks-inbound` & `agent-tasks-completed` |
| **Zookeeper**          | 2181                | Kafka coordination |
| **Ollama**             | 11434               | Serves `llama3` & `nomic-embed-text` models |
| **Pinecone** (SaaS)    | —                   | Index `agent-knowledge-base` (768-dim, cosine metric) |

Full diagrams live in **docs/architecture.md**.

---

## 🧩 Tech Stack

| Layer / Concern       | Technology |
|-----------------------|------------|
| LLM / Embeddings      | **Ollama** (`llama3`, `nomic-embed-text`) |
| Vector Store          | **Pinecone** |
| Messaging Bus         | **Apache Kafka** |
| API Layer             | **FastAPI** |
| Orchestration         | **LangChain** tools & agent |
| Transport (internal)  | **gRPC** (active on 50051) |
| Model Compression     | **PyTorch** 768→256 auto-encoder |
| CI Pipeline           | **GitHub Actions** (containers + tests) |

---

## 📜 Documentation

| File | What you’ll find |
|------|------------------|
| `docs/architecture.md` | Component diagrams & runtime sequence |
| `docs/dev_guide.md`    | Environment setup, commands, CI details |
| `docs/tradeoffs.md`    | Scope boundaries & future paths |

---

## 🧪 CI Status

*Workflow:* **ci.yml**  
*Branch filters:* `main`, `feature/**`, `fix/**`, `chore/**`, `debug/**`  
CI launches Zookeeper, Kafka, Ollama (model preload), both services, then runs unit + integration + E2E tests.

---

## 🙋‍♂️ Author

**Tyler Talbert** — Senior SWE @ Visa  
[LinkedIn](https://www.linkedin.com/in/tylertal) • [GitHub](https://github.com/tyler-talbert)

> This spike is intentionally light—see **docs/tradeoffs.md** for deferred items.
