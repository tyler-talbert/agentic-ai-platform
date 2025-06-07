from app.tools.scholar_tool import ScholarTool
from app.tools.search_tool import SearchTool
from app.logger import setup_logger

log = setup_logger()

class ToolDispatcher:
    def dispatch(self, tool_call: dict) -> dict:
        """Dispatch the tool call to the appropriate handler"""
        tool_name = tool_call.get("tool", "").lower()

        if tool_name == "search":
            return SearchTool().handle(tool_call.get("args", {}))
        elif tool_name == "scholar":
            return ScholarTool().handle(tool_call.get("args", {}))
        else:
            return {"status": "error", "message": f"Unknown tool '{tool_name}'"}
