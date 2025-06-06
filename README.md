[![Maintenance](https://img.shields.io/badge/maintained-yes-brightgreen.svg)](https://github.com/tyler-talbert/agentic-ai-platform)

> 🛠️ This project is under active development and ongoing maintenance.

# agentic-ai-platform
Real-Time Agentic AI Platform built with Python, LangChain, gRPC, Kafka, and vector databases. Enables orchestrated LLM workflows with external knowledge injection (RAG), streaming tasks, and modular service integration.

# 🧠 Agentic AI Platform – Real-Time RAG + Orchestration Stack (LangChain + Kafka + gRPC)

## Overview

This project is a real-time, production-style Agentic AI infrastructure built to showcase a modern stack for scalable Retrieval-Augmented Generation (RAG), agent workflows, and microservice orchestration. Designed with FAANG-level architecture principles, it leverages LangChain, Kafka, gRPC, vector databases, and dynamic routing layers to support complex decision-making powered by AI.

> **Goal**: Simulate a distributed system where an LLM-powered agent ingests user input, retrieves relevant contextual documents, makes routing decisions, and orchestrates task-specific microservices in real time.

---

## ⚙️ Architecture

### Components:

- **Gateway API** (FastAPI / Spring Boot): Handles incoming user prompts and HTTP interaction
- **Agent Orchestrator** (LangChain + Python): Coordinates tools, executes RAG chains, routes to services
- **Knowledge Base** (Vector DB - e.g., FAISS or Qdrant): Embeds and retrieves external data/documents
- **Kafka Broker**: Handles pub/sub events between orchestrator and downstream tools
- **Service Agents**:
  - `CodeAnalyzerService` – Parses and classifies source/target projects
  - `MappingPlannerService` – Plans integration based on metadata
  - `TransformerService` – Applies actual transformations or outputs
- **gRPC Interface**: Enables fast internal calls between Python orchestrator and Java-based services
- **CI/CD**: GitHub Actions for lint/test/build of Python and Java components
- **Local Dev Environment**: Docker Compose

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|------------|
| Language | Python, Java |
| Frameworks | LangChain, FastAPI, Spring Boot |
| Messaging | Apache Kafka |
| Service Mesh | gRPC |
| Vector Search | FAISS / Qdrant |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Auth | JWT (optional layer) |

---

## 🚀 Example Workflow

[User Prompt] → [Gateway API]
↓
[LangChain Agent Orchestrator]
↓
[RAG Chain → Vector DB Search]
↓
[Kafka Publish → Service Agent Request]
↓
[gRPC Call → Java Service Integration]
↓
[Final Response → Gateway → User]


---

## 🔍 Use Cases Simulated

- Integrating source + target projects via LLM
- Auto-generating transformation plans based on external metadata
- Streaming user intents to modular AI agents for fulfillment

---

## 📈 Future Goals

- Add fine-tuning or supervised adapters for specific tools
- Integrate OpenTelemetry for tracing LLM toolchains
- Deploy on Kubernetes with horizontal scaling
- Add observability via Prometheus + Grafana
- Simulate traffic via Locust or k6 for load testing

---

## 👨‍💻 Author

**Tyler Talbert**  
Senior Software Engineer @ Visa  
[LinkedIn](https://www.linkedin.com/in/tylertal)

---

## 🏷️ Tags

`#agentic-ai` `#langchain` `#kafka` `#grpc` `#retrieval` `#vector-db` `#faiss` `#orchestration` `#microservices` `#generative-ai`

