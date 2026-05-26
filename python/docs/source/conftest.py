from __future__ import annotations

from collections import Counter

import pytest
from _pytest.config import Config
from _pytest.terminal import TerminalReporter
from doc_snippet import SYNTAX_CHECKABLE, collect_all_snippets


def pytest_terminal_summary(
    terminalreporter: TerminalReporter,
    exitstatus: int | pytest.ExitCode,
    config: Config,
) -> None:
    all_snippets = collect_all_snippets()
    total_by_language: Counter[str] = Counter()
    tested_by_language: Counter[str] = Counter()

    for snippet in all_snippets:
        total_by_language[snippet.language] += 1
        if snippet.language in SYNTAX_CHECKABLE:
            tested_by_language[snippet.language] += 1

    terminalreporter.section("Documentation Snippet Coverage")
    for lang in sorted(total_by_language):
        total = total_by_language[lang]
        tested = tested_by_language.get(lang, 0)
        marker = "[tested]" if lang in SYNTAX_CHECKABLE else "[recognized]"
        terminalreporter.write_line(f"  {lang}: {tested}/{total} {marker}")

    total_all = sum(total_by_language.values())
    total_tested = sum(tested_by_language.values())
    terminalreporter.write_line("  ---")
    terminalreporter.write_line(f"  Total: {total_tested}/{total_all} snippets syntax-checked")
