import time
import logging
import asyncio

from app.config import SYSTEM_PROMPT
from app.vector_db.vector_db import get_index
from app.vector_db.vector_retriever import retrieve_similar_vectors
from app.llm_interaction import LLMInteraction
from app.agent_runner.tool_call_parser import ToolCallParser
from app.agent_runner.tool_dispatcher import ToolDispatcher

log = logging.getLogger(__name__)

def run_agent(task_id: str, task_input: dict) -> dict:
    log.info(f"[Agent Runner] Running agent for task_id={task_id}, input={task_input}")

    user_input = task_input.get("input") or str(task_input)

    # RAG: retrieve top-5 *answer* contexts from Pinecone
    vector_index = get_index()
    contexts = asyncio.run(retrieve_similar_vectors(user_input, vector_index, top_k=5))
    log.info(f"[Agent Runner] Retrieved {len(contexts)} answer contexts for RAG")

    # Format contexts into prompt using the 'text' metadata
    context_str = "\n\n".join(
        f"Context {i+1} (score={hit['score']:.3f}): {hit['metadata'].get('text','')}"
        for i, hit in enumerate(contexts)
    )
    prompt_text = f"{context_str}\n\nUser: {user_input}"

    # Invoke the LLM
    llm = LLMInteraction(system_prompt=SYSTEM_PROMPT)
    response_content = llm.run(prompt_text)
    log.info(f"[Agent Runner] LLM response: {response_content}")

    # Tool parsing / dispatch as before
    parser = ToolCallParser()
    tool_call = parser.parse(response_content)

    if tool_call:
        log.info(f"[Agent Runner] Tool call detected: {tool_call}")
        dispatcher = ToolDispatcher()
        tool_response = dispatcher.dispatch(tool_call)
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
