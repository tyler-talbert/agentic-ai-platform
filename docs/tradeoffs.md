# ⚖️ Trade-Offs & Scope Boundaries

This spike is tuned for interview review, not production.  
Everything included below directly supports that goal.

---

## What’s In ✅

* End-to-end RAG flow with local LLM (ChatOllama)  
* Kafka-backed task orchestration  
* Pinecone vector search (768-dim)  
* **768→256 auto-encoder** with training script & runtime loading  
* Complete synchronous gRPC path (`RunTask` on 50051)  
* Green CI: unit + integration + E2E tests  
* Diagrams and developer docs

These pieces prove architectural depth yet fit into a 30-minute walkthrough.

---

## Deferred (by design) 🚫

| Area | Rationale | Upgrade Path |
|------|-----------|--------------|
| **Continuous Delivery** | Local run suffices; deploy infra would double repo size. | GHCR push + Helm charts |
| **Observability** | Extra containers, minimal interview value. | OTLP export → Prom/Grafana |
| **Auth / Gateway** | Security is outside this learning objective. | JWT middleware or Kong |
| **Advanced LLM Fine-Tuning** | Model-level tuning (LoRA, QLoRA) increases GPU demand. | Colab notebook + HF dataset |
