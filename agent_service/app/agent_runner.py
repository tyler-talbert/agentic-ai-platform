from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

def run_agent(task_input: dict) -> str:
    prompt_text = task_input["input"] if "input" in task_input else str(task_input)

    model = ChatOllama(
        model="llama3",  # or "mistral"
        temperature=0.7
    )

    response = model.invoke([HumanMessage(content=prompt_text)])
    return response.content
