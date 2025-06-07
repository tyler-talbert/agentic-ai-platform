import time
import logging
from app.llm_interaction import LLMInteraction
from app.agent_runner.tool_call_parser import ToolCallParser
from app.agent_runner.tool_dispatcher import ToolDispatcher
from app.config import SYSTEM_PROMPT  # Import system prompt from config

log = logging.getLogger(__name__)


def run_agent(task_id: str, task_input: dict) -> dict:
    log.info(f"[Agent Runner] Running agent for task_id={task_id}, input={task_input}")

    # Extract the prompt from task input
    prompt_text = task_input.get("input") or str(task_input)

    # Step 1: Initialize LLM Interaction and get the response
    llm_interaction = LLMInteraction(system_prompt=SYSTEM_PROMPT)
    response_content = llm_interaction.run(prompt_text)

    log.info(f"[Agent Runner] Response: {response_content}")

    # Step 2: Parse the response content for tool calls
    tool_call_parser = ToolCallParser()
    tool_call = tool_call_parser.parse(response_content)

    if tool_call:
        log.info(f"[Agent Runner] Tool call detected: {tool_call}")

        # Step 3: Dispatch the tool call to the appropriate handler
        tool_dispatcher = ToolDispatcher()
        tool_response = tool_dispatcher.dispatch(tool_call)

        return {
            "task_id": task_id,
            "status": "COMPLETED",
            "output": tool_response,
            "timestamp": time.time()
        }

    # If no tool call, return the raw response from the LLM
    log.info("[Agent Runner] No tool call found, returning LLM output.")
    return {
        "task_id": task_id,
        "status": "COMPLETED",
        "output": response_content,
        "timestamp": time.time()
    }