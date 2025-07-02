# 🏗️ Architecture — Agentic AI Platform

## 1 · Logical View

~~~text
                                   ┌───────────────────────┐
User ── HTTP POST /v1/tasks ──► 4000 │  Orchestrator (FastAPI)│
                                   └────────┬──────────────┘
                                            │ synchronous gRPC
                                            ▼
                            ┌────────────────────────────────────────┐
                            │        Agent Service (gRPC)           │
                            │  • embeds & retrieves (Pinecone)      │
                            │  • ChatOllama LLM (llama3)            │
                            │  • publishes result to Kafka          │
                            └────────┬──────────────┬───────────────┘
                                     │              │
                                     │              │ Kafka publish
                                     │              ▼
                                     │       ┌───────────────┐
                                     │       │ kafka topic   │
                                     │       │ completed     │
                                     │       └───────────────┘
                                     ▼
                            ┌───────────────────────┐
                            │    Pinecone Index     │
                            └───────────────────────┘
~~~

**Step Legend**

1. Orchestrator generates task ID, embeds prompt, upserts vector to Pinecone.  
2. Orchestrator calls `RunTask` via gRPC with a 15-second deadline.  
3. Agent performs RAG, returns `COMPLETED` reply, and publishes result to `agent-tasks-completed`.  
4. Orchestrator’s Kafka consumer updates `TASK_STORE`; user polls GET `/v1/tasks/{id}` for the answer.

---

## 2 · Deployment Topology (Local)

~~~text
Docker bridge network
├─ orchestrator  :4000
├─ agent_service :4001 (HTTP) / 50051 (gRPC)
├─ kafka         :9092
├─ zookeeper     :2181
├─ ollama        :11434
└─ pinecone      (SaaS endpoint)
~~~

---

## 3 · Extension Points

| Future Need | Plug-in Path |
|-------------|-------------|
| Swap local LLM for OpenAI GPT | Update `OLLAMA_BASE_URL` & model names |
| Replace Pinecone with Qdrant | Implement alternate client in `vector_db.py` |
| Add new micro-agents | Additional gRPC methods or extra Kafka topics |
