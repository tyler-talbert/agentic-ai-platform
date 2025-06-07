import json
import re
from typing import Optional, Dict, Any
from app.logger import setup_logger

log = setup_logger()

class ToolCallParser:
    def parse(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse tool call from LLM response"""
        log.info(f"[Tool Call Parser] Parsing response: {response_text[:500]}...")

        tool_call = self.extract_from_code_blocks(response_text)
        if tool_call:
            return tool_call

        tool_call = self.extract_from_raw_json(response_text)
        if tool_call:
            return tool_call

        tool_call = self.extract_from_patterns(response_text)
        if tool_call:
            return tool_call

        log.warning("[Tool Call Parser] No valid tool call found in LLM response")
        return None

    def extract_from_code_blocks(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract tool calls from JSON code blocks"""
        json_code_pattern = r"```json\s*(.*?)\s*```"
        matches = re.findall(json_code_pattern, response_text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            tool_call = self.try_parse_json_content(match.strip())
            if tool_call:
                log.info(f"[Tool Call Parser] Found tool call in JSON code block")
                return tool_call

        generic_code_pattern = r"```\s*(.*?)\s*```"
        matches = re.findall(generic_code_pattern, response_text, re.DOTALL)

        for match in matches:
            if any(keyword in match.lower() for keyword in ['def ', 'import ', 'class ', 'function']):
                continue

            tool_call = self.try_parse_json_content(match.strip())
            if tool_call:
                log.info(f"[Tool Call Parser] Found tool call in generic code block")
                return tool_call

        return None

    def extract_from_raw_json(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract tool calls from raw JSON objects"""
        json_objects = self.find_json_objects(response_text)

        for json_str in json_objects:
            tool_call = self.try_parse_json_content(json_str)
            if tool_call:
                log.info(f"[Tool Call Parser] Found tool call in raw JSON")
                return tool_call

        return None

    def extract_from_patterns(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract tool calls using pattern matching for common formats"""
        patterns = [
            r'"tool":\s*"(\w+)"\s*,\s*"arguments?":\s*(\{[^}]*\})',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if len(match) == 2:
                    tool_name, args_str = match
                    try:
                        args = json.loads(args_str)
                        return {
                            "tool": tool_name,
                            "args": args
                        }
                    except json.JSONDecodeError:
                        continue

        return None

    def find_json_objects(self, text: str) -> list:
        """Find all potential JSON objects using balanced brace matching"""
        json_objects = []
        i = 0

        while i < len(text):
            if text[i] == '{':
                brace_count = 1
                start = i
                i += 1

                while i < len(text) and brace_count > 0:
                    if text[i] == '{':
                        brace_count += 1
                    elif text[i] == '}':
                        brace_count -= 1
                    i += 1

                if brace_count == 0:
                    json_candidate = text[start:i]
                    json_objects.append(json_candidate)
            else:
                i += 1

        return json_objects

    def try_parse_json_content(self, content: str) -> Optional[Dict[str, Any]]:
        """Try to parse JSON content and validate it as a tool call"""
        if not content or not content.strip():
            return None

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError as e:
            log.debug(f"[Tool Call Parser] JSON decode error: {e}")
        return None
