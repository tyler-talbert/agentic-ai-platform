import time
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
from app.logger import setup_logger

log = setup_logger()
load_dotenv()


def run_agent(task_id: str, task_input: dict) -> dict:
    log.info(f"[Agent Runner] Running agent for task_id={task_id}, input={task_input}")

    prompt_text = task_input.get("input") or str(task_input)

    model = ChatOllama(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3:latest"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
    )

    response = model.invoke([HumanMessage(content=prompt_text)])

    log.info(f"[Agent Runner] Response: {response.content}")

    return {
        "task_id": task_id,
        "status": "COMPLETED",
        "output": response.content,
        "timestamp": time.time()
    }

