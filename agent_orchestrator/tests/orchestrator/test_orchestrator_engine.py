import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.orchestrator.orchestrator_engine import OrchestrationEngine


@pytest.mark.asyncio
@patch("app.orchestrator.orchestrator_engine.produce_task")                 # stub Kafka
@patch("app.orchestrator.orchestrator_engine.embed_text", new_callable=AsyncMock)
async def test_handle_task_embeds_and_upserts(mock_embed, mock_produce):
    mock_embed.return_value = [0.5] * 1536
    mock_index = MagicMock()

    task_input = {"input": "test input"}
    task       = await OrchestrationEngine.handle_task(task_input, vector_index=mock_index)

    assert task.input == task_input
    mock_index.upsert.assert_called_once()
    mock_produce.assert_called_once_with(task)
