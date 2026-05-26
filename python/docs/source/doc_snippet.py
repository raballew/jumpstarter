from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass

import pytest
import yaml

DOCS_DIR = os.path.join(os.path.dirname(__file__))

SKIP_DIRECTIVES = frozenset(
    [
        "mermaid",
        "toctree",
        "glossary",
        "raw",
        "eval-rst",
        "include",
        "note",
        "warning",
        "tip",
        "tab",
    ]
)

RECOGNIZED_LANGUAGES = frozenset(
    [
        "python",
        "yaml",
        "bash",
        "console",
        "shell",
        "json",
        "toml",
        "ini",
        "protobuf",
        "promql",
        "text",
        "kotlin",
        "typescript",
    ]
)

SYNTAX_CHECKABLE = frozenset(["python", "yaml", "bash", "console"])


@dataclass(frozen=True)
class Snippet:
    language: str
    content: str
    file_path: str
    line_number: int


def _normalize_language(raw_lang: str) -> str:
    lang = raw_lang.strip().lower()
    if lang in ("sh", "shell"):
        return "bash"
    return lang


def _is_skip_directive(tag: str) -> bool:
    cleaned = tag.strip().strip("{}")
    return cleaned in SKIP_DIRECTIVES


def _skip_option_lines(lines: list[str], start: int, end_marker: str) -> int:
    i = start
    while i < len(lines) and not lines[i].strip().startswith(end_marker):
        stripped = lines[i].strip()
        if stripped.startswith(":") and ":" in stripped[1:]:
            i += 1
        else:
            break
    return i


def _read_block_content(lines: list[str], start: int, fence_marker: str) -> tuple[str, int]:
    content_lines = []
    i = start
    while i < len(lines) and lines[i].strip() != fence_marker:
        content_lines.append(lines[i])
        i += 1
    return "".join(content_lines), i


@dataclass(frozen=True)
class FenceOpening:
    marker: str
    language: str
    is_directive: bool


def _parse_fence_opening(stripped: str) -> FenceOpening | None:
    match = re.match(r"^(`{3,})\{testcode\}\s*$", stripped)
    if match:
        return FenceOpening(marker=match.group(1), language="testcode", is_directive=True)

    match = re.match(r"^(`{3,})\{code-block\}\s+(\S+)\s*$", stripped)
    if match:
        return FenceOpening(marker=match.group(1), language=match.group(2), is_directive=True)

    match = re.match(r"^(`{3,})(\w[\w+-]*)\s*$", stripped)
    if match:
        return FenceOpening(marker=match.group(1), language=match.group(2), is_directive=False)

    return None


def extract_snippets(file_path: str) -> list[Snippet]:
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    snippets: list[Snippet] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        if stripped.startswith("````{tab}"):
            i += 1
            continue

        parsed = _parse_fence_opening(stripped)
        if not parsed:
            i += 1
            continue

        fence_marker = parsed.marker
        raw_lang = parsed.language
        lang = "python" if raw_lang == "testcode" else _normalize_language(raw_lang)

        if _is_skip_directive(raw_lang):
            _, i = _read_block_content(lines, i + 1, fence_marker)
            i += 1
            continue

        if parsed.is_directive:
            i = _skip_option_lines(lines, i + 1, fence_marker)
        else:
            i += 1
        start_line = i
        content, i = _read_block_content(lines, i, fence_marker)

        if content.strip() and lang in RECOGNIZED_LANGUAGES:
            snippets.append(
                Snippet(language=lang, content=content, file_path=file_path, line_number=start_line + 1)
            )
        i += 1

    return snippets


def _replace_myst_substitutions(text: str) -> str:
    return re.sub(r"\{\{(\w+)\}\}", r"PLACEHOLDER_\1", text)


def _replace_angle_bracket_placeholders(text: str) -> str:
    return re.sub(r"<[\w\s-]+>", "PLACEHOLDER", text)


def validate_python(snippet: Snippet) -> None:
    try:
        compile(snippet.content, snippet.file_path, "exec")
    except SyntaxError as exc:
        lineno = exc.lineno or 0
        pytest.fail(
            f"Python syntax error in {snippet.file_path}:{snippet.line_number + lineno - 1}: {exc.msg}"
        )


def validate_yaml(snippet: Snippet) -> None:
    content = _replace_myst_substitutions(snippet.content)
    try:
        list(yaml.safe_load_all(content))
    except yaml.YAMLError as exc:
        pytest.fail(
            f"YAML parse error in {snippet.file_path}:{snippet.line_number}: {exc}"
        )


def _extract_bash_commands(content: str) -> str:
    result_lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("$ "):
            cmd = stripped[2:]
            result_lines.append(cmd)
        elif result_lines and result_lines[-1].endswith("\\"):
            result_lines.append(stripped)
    return "\n".join(result_lines) if result_lines else ""


def _looks_like_usage_output(content: str) -> bool:
    lines = content.strip().splitlines()
    if not lines:
        return False
    first = lines[0].strip()
    return first.startswith("Usage:") or first.startswith("usage:")


def validate_bash(snippet: Snippet) -> None:
    if snippet.language == "console":
        commands = _extract_bash_commands(snippet.content)
    elif snippet.language == "bash" and _looks_like_usage_output(snippet.content):
        return
    else:
        commands = snippet.content

    commands = _replace_myst_substitutions(commands)
    commands = _replace_angle_bracket_placeholders(commands)

    if not commands.strip():
        return

    try:
        result = subprocess.run(
            ["bash", "-n"],
            input=commands,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(
            f"Bash syntax check timed out in {snippet.file_path}:{snippet.line_number}"
        )
    if result.returncode != 0:
        pytest.fail(
            f"Bash syntax error in {snippet.file_path}:{snippet.line_number}: {result.stderr.strip()}"
        )


VALIDATORS: dict[str, Callable[[Snippet], None]] = {
    "python": validate_python,
    "yaml": validate_yaml,
    "bash": validate_bash,
    "console": validate_bash,
}


def collect_all_snippets() -> list[Snippet]:
    all_snippets = []
    for root, _dirs, files in os.walk(DOCS_DIR):
        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            all_snippets.extend(extract_snippets(fpath))
    return all_snippets


def _snippet_id(snippet: Snippet) -> str:
    rel = os.path.relpath(snippet.file_path, DOCS_DIR)
    return f"{rel}:{snippet.line_number}:{snippet.language}"


def _get_syntax_checkable_snippets() -> list[Snippet]:
    return [s for s in collect_all_snippets() if s.language in SYNTAX_CHECKABLE]
