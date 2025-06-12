import unittest
import asyncio
import unittest.mock
from typing import List, Dict

from agent_service.app.vector_db.vector_retriever import retrieve_similar_vectors

class DummyMatch:
    def __init__(self, _id: str, score: float, metadata: Dict):
        self.id = _id
        self.score = score
        self.metadata = metadata

class DummyResult:
    def __init__(self, matches: List[DummyMatch]):
        self.matches = matches

class DummyIndex:
    def __init__(self, result: DummyResult):
        self._result = result

    def query(self, namespace, vector, top_k, include_metadata, filter, score_threshold=None):
        self.received_threshold = score_threshold
        return self._result

class TestVectorRetriever(unittest.TestCase):
    def setUp(self):
        patcher = unittest.mock.patch(
            'agent_service.app.vector_db.vector_retriever.embed_text',
            new=self.fake_embed_text
        )
        self.addCleanup(patcher.stop)
        patcher.start()

        matches = [
            DummyMatch('q1-a', 0.95, {'type': 'answer', 'task_id': 'q1', 'text': 'Answer1'}),
            DummyMatch('q2-a', 0.85, {'type': 'answer', 'task_id': 'q2', 'text': 'Answer2'}),
        ]
        self.index = DummyIndex(DummyResult(matches))

    async def fake_embed_text(self, text: str) -> List[float]:
        return [0.1, 0.2, 0.3]

    def test_retrieve_similar_vectors(self):
        contexts = asyncio.get_event_loop().run_until_complete(
            retrieve_similar_vectors("dummy query", self.index, top_k=2)
        )
        self.assertEqual(len(contexts), 2)
        self.assertEqual(contexts[0]['id'], 'q1-a')
        self.assertAlmostEqual(contexts[0]['score'], 0.95)
        self.assertEqual(contexts[0]['metadata']['text'], 'Answer1')
        self.assertEqual(contexts[1]['id'], 'q2-a')
        self.assertAlmostEqual(contexts[1]['score'], 0.85)
        self.assertEqual(contexts[1]['metadata']['text'], 'Answer2')

    def test_retrieve_respects_threshold(self):
        contexts = asyncio.get_event_loop().run_until_complete(
            retrieve_similar_vectors(
                "dummy query",
                self.index,
                top_k=2,
                relevance_threshold=0.9,
            )
        )
        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts[0]['id'], 'q1-a')
        self.assertAlmostEqual(contexts[0]['score'], 0.95)