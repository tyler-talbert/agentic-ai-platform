import unittest
from app.tools.scholar_tool import ScholarTool


class TestScholarTool(unittest.TestCase):
    def setUp(self):
        self.tool = ScholarTool()

    def test_handle(self):
        args = {"query": "artificial intelligence", "result_type": "latest", "count": 5}
        result = self.tool.handle(args)

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 5)
        self.assertTrue("Scholar paper" in result["results"][0])


if __name__ == "__main__":
    unittest.main()
