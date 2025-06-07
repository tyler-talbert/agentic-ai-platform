import time
import logging
from app.llm_interaction import LLMInteraction
from app.agent_runner.tool_call_parser import ToolCallParser
from app.agent_runner.tool_dispatcher import ToolDispatcher
from app.config import SYSTEM_PROMPT

log = logging.getLogger(__name__)


def run_agent(task_id: str, task_input: dict) -> dict:
    log.info(f"[Agent Runner] Running agent for task_id={task_id}, input={task_input}")

    prompt_text = task_input.get("input") or str(task_input)

    llm_interaction = LLMInteraction(system_prompt=SYSTEM_PROMPT)
    response_content = llm_interaction.run(prompt_text)

    log.info(f"[Agent Runner] Response: {response_content}")

    tool_call_parser = ToolCallParser()
    tool_call = tool_call_parser.parse(response_content)

    if tool_call:
        log.info(f"[Agent Runner] Tool call detected: {tool_call}")

        tool_dispatcher = ToolDispatcher()
        tool_response = tool_dispatcher.dispatch(tool_call)

        return {
            "task_id": task_id,
            "status": "COMPLETED",
            "output": tool_response,
            "timestamp": time.time()
        }

    log.info("[Agent Runner] No tool call found, returning LLM output.")
    return {
        "task_id": task_id,
        "status": "COMPLETED",
        "output": response_content,
        "timestamp": time.time()
    }