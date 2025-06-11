import unittest
from agent_service.app.tools.search_tool import SearchTool

class TestSearchTool(unittest.TestCase):
    def setUp(self):
        self.tool = SearchTool()

    def test_handle(self):
        args = {"query": "machine learning"}
        result = self.tool.handle(args)

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 3)
        self.assertTrue("Search result" in result["results"][0])

if __name__ == "__main__":
    unittest.main()
