"""Client-side preview count only. The API does the real parsing."""
import re

AC_PATTERN = re.compile(r"^AC\d+:", re.MULTILINE)


def count_criteria(text: str) -> int:
    return len(AC_PATTERN.findall(text))