import pytest
from unittest.mock import MagicMock, patch
from app.orchestrator.orchestrator_engine import OrchestrationEngine
from app.orchestrator.task_store import TASK_STORE
import asyncio

@pytest.mark.asyncio
@patch("app.orchestrator.orchestrator_engine.produce_task")  # stub Kafka
async def test_handle_task_produces_task(mock_produce):
    request = MagicMock()

    task_input = {"input": "test input"}

    task = await OrchestrationEngine.handle_task(task_input, request)

    await asyncio.sleep(0)

    assert task.input == task_input
    assert TASK_STORE[task.id] is task
    mock_produce.assert_called_once_with(task)
