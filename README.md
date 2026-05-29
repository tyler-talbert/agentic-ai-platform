# Agentic AI Platform

Two-service Docker Compose spike: RAG with local LLMs, Pinecone for vector search, a 768→256 autoencoder for compressed embeddings, and Kafka for task orchestration. Built to play with the architecture, not for production.

## Quick start

```bash
git clone https://github.com/tyler-talbert/agentic-ai-platform.git
cd agentic-ai-platform
docker compose up    # orchestrator, agent, Kafka, Zookeeper, Ollama
```

Create a task:

```bash
curl -X POST http://localhost:4000/v1/tasks \
     -H "Content-Type: application/json" \
     -d '{"input": "Who won the 2024 NBA Finals?"}'
```

Poll for status:

```bash
curl http://localhost:4000/v1/tasks/<TASK_ID>
```

## gRPC

```bash
grpcurl -plaintext \
  -d '{"task_id":"demo","payload":"ping"}' \
  localhost:50051 agent.AgentService/RunTask
```

If you get `server does not support the reflection API`, rebuild so `grpcio-reflection` is installed: `docker compose up --build`.

Windows cmd.exe, single line with escaped quotes:

```cmd
.\grpcurl.exe -plaintext -d "{\"task_id\":\"123\",\"payload\":\"ping\"}" localhost:50051 agent.AgentService/RunTask
```

Expect a `COMPLETED` reply with the LLM output.

## Autoencoder runtime flags

| Variable                    | Default                     | Description                                          |
| --------------------------- | --------------------------- | ---------------------------------------------------- |
| `AUTOENCODER_WEIGHTS`       | `autoencoder.pt`            | PyTorch weights for 256-dim encoding                 |
| `PINECONE_COMPRESSED_INDEX` | `agent-knowledge-base-256`  | 256-dim Pinecone index for compressed vectors        |
| `RELEVANCE_THRESHOLD`       | `0.75`                      | Similarity cutoff after retrieval                    |

Train your own weights:

```bash
python -m agent_service.app.pytorch.train_autoencoder \
       --sample-size 5000 --epochs 3
```

Then back-fill the compressed index with `backfill_encoded_vectors.py`.

## Architecture

| Component            | Host port(s)   | Purpose                                                                                                  |
| -------------------- | -------------- | -------------------------------------------------------------------------------------------------------- |
| `agent_orchestrator` | 4000           | REST API (`/v1/tasks`, `/health`, `/run-agent`); embeds prompt, upserts to Pinecone; produces to Kafka; sync gRPC calls |
| `agent_service`      | 4001, 50051    | FastAPI debug endpoint (4001); gRPC server (50051); consumes tasks, runs RAG, publishes results          |
| Kafka                | 9092           | Topics `agent-tasks-inbound` and `agent-tasks-completed`                                                  |
| Zookeeper            | 2181           | Kafka coordination                                                                                       |
| Ollama               | 11434          | Serves `llama3` and `nomic-embed-text`                                                                   |
| Pinecone (SaaS)      | —              | Index `agent-knowledge-base` (768-dim, cosine)                                                           |

Full diagrams in `docs/architecture.md`.

## Stack

| Layer              | Tech                                          |
| ------------------ | --------------------------------------------- |
| LLM / embeddings   | Ollama (`llama3`, `nomic-embed-text`)         |
| Vector store       | Pinecone                                      |
| Messaging          | Apache Kafka                                  |
| API                | FastAPI                                       |
| Orchestration      | LangChain tools and agent                     |
| Internal transport | gRPC (50051)                                  |
| Model compression  | PyTorch 768→256 autoencoder                   |
| CI                 | GitHub Actions (containers + tests)           |

## Docs

| File                    | Contents                                |
| ----------------------- | --------------------------------------- |
| `docs/architecture.md`  | Component diagrams, runtime sequence    |
| `docs/dev_guide.md`     | Environment setup, commands, CI details |
| `docs/tradeoffs.md`     | Scope boundaries and future paths       |

## CI

Workflow: `ci.yml`. Branches: `main`, `feature/**`, `fix/**`, `chore/**`, `debug/**`. CI launches Zookeeper, Kafka, Ollama (with model preload), both services, then runs unit, integration, and E2E tests.

## Author

Tyler Talbert — [LinkedIn](https://www.linkedin.com/in/tylertal) · [GitHub](https://github.com/tyler-talbert)

Spike is intentionally light — see `docs/tradeoffs.md` for deferred items.
