import unittest
from unittest.mock import patch
import os

from agent_orchestrator.app.vector_db.vector_db import init_pinecone, create_index, get_index

class TestVectorDB(unittest.TestCase):

    @patch("pinecone.init")
    def test_init_pinecone(self, mock_init):
        os.environ["PINECONE_API_KEY"] = "test-key"
        os.environ["PINECONE_ENV"] = "test-env"
        init_pinecone()
        mock_init.assert_called_with(api_key="test-key", environment="test-env")

    @patch("pinecone.list_indexes", return_value=["existing-index"])
    @patch("pinecone.create_index")
    def test_create_index_existing(self, mock_create_index, mock_list_indexes):
        create_index("existing-index", 128)
        mock_create_index.assert_not_called()

    @patch("pinecone.list_indexes", return_value=[])
    @patch("pinecone.create_index")
    def test_create_index_new(self, mock_create_index, mock_list_indexes):
        create_index("new-index", 128)
        mock_create_index.assert_called_with("new-index", dimension=128)

    @patch("pinecone.Index")
    def test_get_index_success(self, mock_index_class):
        index = get_index("some-index")
        mock_index_class.assert_called_with("some-index")
        self.assertIsNotNone(index)

    @patch("pinecone.Index", side_effect=Exception("Failure"))
    def test_get_index_failure(self, mock_index_class):
        index = get_index("bad-index")
        self.assertIsNone(index)

if __name__ == "__main__":
    unittest.main()
