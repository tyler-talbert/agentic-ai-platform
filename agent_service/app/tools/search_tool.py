import logging

log = logging.getLogger(__name__)

class SearchTool:
    def handle(self, args: dict) -> dict:
        query = args.get("query", "")
        log.info(f"[Search Tool] Executing search for: {query}")

        return {
            "status": "success",
            "results": [
                f"Search result 1 for '{query}'",
                f"Search result 2 for '{query}'"
            ]
        }
