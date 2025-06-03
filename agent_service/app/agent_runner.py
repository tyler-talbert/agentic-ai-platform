from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

def run_agent(task_input: dict) -> str:
    print(f"[Agent Runner] Received task input: {task_input}", flush=True)
    prompt_text = task_input["input"] if "input" in task_input else str(task_input)

    model = ChatOllama(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3:latest"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
    )

    response = model.invoke([HumanMessage(content=prompt_text)])
    print(f"[Agent Runner] Final response: {response}", flush=True)
    return response.content
