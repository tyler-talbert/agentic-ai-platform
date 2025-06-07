import time
import json
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
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
    )

    response = model.invoke([HumanMessage(content=prompt_text)])

    log.info(f"[Agent Runner] Response: {response.content}")


    tool_call = _parse_tool_call(response.content)
    if tool_call:
        output = _dispatch_tool(tool_call)
    else:
        output = {
            "status": "error",
            "message": "Unable to parse tool call",
            "llm_response": response.content,
        }

    return {
        "task_id": task_id,
        "status": "COMPLETED",
        "output": output,
        "timestamp": time.time(),
    }


def _parse_tool_call(response_text: str) -> dict | None:
    import json
    import re

    code_match = re.search(r"```(.*?)```", response_text, re.DOTALL)
    raw = code_match.group(1) if code_match else None
    if not raw:
        brace_match = re.search(r"{.*}", response_text, re.DOTALL)
        raw = brace_match.group(0) if brace_match else None
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        log.info("[Agent Runner] Failed to decode tool JSON")
        return None


def _dispatch_tool(tool_call: dict) -> dict:
    tool = tool_call.get("tool")
    if tool == "search":
        query = tool_call.get("query", "")
        return _search_tool(query)
    return {"status": "error", "message": f"Unknown tool '{tool}'"}


def _search_tool(query: str) -> dict:
    return {"status": "success", "results": [f"Result for {query}"]}




