import os
import unittest
from unittest.mock import patch, MagicMock
from app.vector_db.vector_db import init_pinecone, create_index, get_index


class TestVectorDB(unittest.TestCase):

    @patch("app.vector_db.vector_db.Pinecone")
    def test_init_pinecone_no_error(self, mock_pc):
        os.environ["PINECONE_API_KEY"] = "dummy"
        os.environ["PINECONE_ENV"] = "dummy"
        init_pinecone()           # should not raise

    @patch("app.vector_db.vector_db.Pinecone")
    def test_create_index_existing(self, mock_pc_cls):
        mock_client = MagicMock()
        mock_client.list_indexes().names.return_value = ["existing"]
        mock_pc_cls.return_value = mock_client
        create_index("existing", 128)

    @patch("app.vector_db.vector_db.Pinecone")
    def test_create_index_new(self, mock_pc_cls):
        mock_client = MagicMock()
        mock_client.list_indexes().names.return_value = []
        mock_pc_cls.return_value = mock_client
        create_index("new‑index", 128)
        mock_client.create_index.assert_called_once()

    @patch("app.vector_db.vector_db.Pinecone")
    def test_get_index_success(self, mock_pc_cls):
        mock_client = MagicMock()
        mock_idx = MagicMock()
        mock_client.Index.return_value = mock_idx
        mock_pc_cls.return_value = mock_client
        self.assertIs(get_index("my‑idx"), mock_idx)

    @patch("app.vector_db.vector_db.Pinecone")
    def test_get_index_failure(self, mock_pc_cls):
        mock_client = MagicMock()
        mock_client.Index.side_effect = Exception("boom")
        mock_pc_cls.return_value = mock_client
        with self.assertRaises(Exception):
            get_index("bad‑idx")
