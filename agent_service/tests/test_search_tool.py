import unittest
from app.tools.search_tool import SearchTool


class TestSearchTool(unittest.TestCase):
    def setUp(self):
        self.tool = SearchTool()

    def test_handle(self):
        # Test with mock input
        args = {"query": "machine learning"}
        result = self.tool.handle(args)

        # Check if the result is as expected
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 3)
        self.assertTrue("Search result" in result["results"][0])


if __name__ == "__main__":
    unittest.main()
