"""
SQL String Sanitizer.
Normalizes raw LLM textual output into an executable SQL string.
"""
import re


class SQLSanitizer:
    @staticmethod
    def sanitize(raw_text: str) -> str:
        """
        Strips markdown blocks, trailing commentary, and excess whitespace.
        """
        if not raw_text or not raw_text.strip():
            return ""

        text = raw_text.strip()

        # Extract content inside ```sql ... ``` or ``` ... ``` if present
        markdown_match = re.search(r"```(?:sql)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if markdown_match:
            text = markdown_match.group(1).strip()

        # Remove single-line comments (-- ...) that could mask injections
        # but retain legitimate string contents
        lines = [line for line in text.splitlines() if not line.strip().startswith("--")]
        text = "\n".join(lines).strip()

        # Remove leading/trailing quotes or backticks if emitted accidentally
        text = text.strip("`'\"")

        return text.strip()


sql_sanitizer = SQLSanitizer()