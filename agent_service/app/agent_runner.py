from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

def run_agent(task_input: dict) -> str:
    prompt_text = task_input["input"] if "input" in task_input else str(task_input)

    model = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
    )

    response = model.invoke([HumanMessage(content=prompt_text)])
    return response.content
