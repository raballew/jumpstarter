import os
import re
import subprocess
import textwrap
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
    while i < len(lines) and not lines[i].strip().startswith(fence_marker):
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


class TestNormalizeLanguage:
    def test_sh_maps_to_bash(self):
        assert _normalize_language("sh") == "bash"

    def test_shell_maps_to_bash(self):
        assert _normalize_language("shell") == "bash"

    def test_python_unchanged(self):
        assert _normalize_language("python") == "python"

    def test_uppercase_is_lowered(self):
        assert _normalize_language("YAML") == "yaml"

    def test_whitespace_is_stripped(self):
        assert _normalize_language("  python  ") == "python"

    def test_shell_uppercase_maps_to_bash(self):
        assert _normalize_language("Shell") == "bash"


class TestIsSkipDirective:
    def test_mermaid_is_skip(self):
        assert _is_skip_directive("mermaid") is True

    def test_toctree_is_skip(self):
        assert _is_skip_directive("toctree") is True

    def test_python_is_not_skip(self):
        assert _is_skip_directive("python") is False

    def test_braces_are_stripped(self):
        assert _is_skip_directive("{mermaid}") is True

    def test_whitespace_and_braces_stripped(self):
        assert _is_skip_directive("  {note}  ") is True

    def test_all_skip_directives_recognized(self):
        for directive in SKIP_DIRECTIVES:
            assert _is_skip_directive(directive) is True


class TestParseFenceOpening:
    def test_standard_python_fence(self):
        result = _parse_fence_opening("```python")
        assert result == FenceOpening(marker="```", language="python", is_directive=False)

    def test_testcode_directive(self):
        result = _parse_fence_opening("```{testcode}")
        assert result == FenceOpening(marker="```", language="testcode", is_directive=True)

    def test_code_block_directive(self):
        result = _parse_fence_opening("```{code-block} yaml")
        assert result == FenceOpening(marker="```", language="yaml", is_directive=True)

    def test_four_backtick_fence(self):
        result = _parse_fence_opening("````python")
        assert result == FenceOpening(marker="````", language="python", is_directive=False)

    def test_non_fence_line_returns_none(self):
        assert _parse_fence_opening("some text") is None

    def test_empty_backticks_return_none(self):
        assert _parse_fence_opening("```") is None

    def test_language_with_plus_chars(self):
        result = _parse_fence_opening("```c++")
        assert result is not None
        assert result.language == "c++"
        assert result.is_directive is False

    def test_language_with_hyphen(self):
        result = _parse_fence_opening("```objective-c")
        assert result is not None
        assert result.language == "objective-c"
        assert result.is_directive is False


class TestSkipOptionLines:
    def test_single_option_line(self):
        lines = [":skipif: True\n", "code here\n", "```\n"]
        result = _skip_option_lines(lines, 0, "```")
        assert result == 1

    def test_multiple_option_lines(self):
        lines = [":skipif: True\n", ":substitutions:\n", "code here\n", "```\n"]
        result = _skip_option_lines(lines, 0, "```")
        assert result == 2

    def test_non_option_stops_skipping(self):
        lines = ["code here\n", ":skipif: True\n", "```\n"]
        result = _skip_option_lines(lines, 0, "```")
        assert result == 0

    def test_end_marker_stops_skipping(self):
        lines = [":skipif: True\n", "```\n"]
        result = _skip_option_lines(lines, 0, "```")
        assert result == 1

    def test_end_marker_encountered_during_options(self):
        lines = ["```\n"]
        result = _skip_option_lines(lines, 0, "```")
        assert result == 0

    def test_empty_lines_list(self):
        result = _skip_option_lines([], 0, "```")
        assert result == 0

    def test_start_beyond_end(self):
        lines = [":skipif: True\n"]
        result = _skip_option_lines(lines, 5, "```")
        assert result == 5


class TestReadBlockContent:
    def test_reads_until_fence_marker(self):
        lines = ["line 1\n", "line 2\n", "```\n", "after\n"]
        content, end = _read_block_content(lines, 0, "```")
        assert content == "line 1\nline 2\n"
        assert end == 2

    def test_reads_to_end_of_file_when_no_marker(self):
        lines = ["line 1\n", "line 2\n"]
        content, end = _read_block_content(lines, 0, "```")
        assert content == "line 1\nline 2\n"
        assert end == 2

    def test_empty_block(self):
        lines = ["```\n"]
        content, end = _read_block_content(lines, 0, "```")
        assert content == ""
        assert end == 0

    def test_start_offset(self):
        lines = ["skip\n", "line 1\n", "```\n"]
        content, end = _read_block_content(lines, 1, "```")
        assert content == "line 1\n"
        assert end == 2

    def test_four_backtick_fence(self):
        lines = ["line 1\n", "````\n"]
        content, end = _read_block_content(lines, 0, "````")
        assert content == "line 1\n"
        assert end == 1


class TestExtractSnippets:
    def test_extracts_fenced_python_block(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            # Title

            ```python
            x = 1
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 1
        assert snippets[0].language == "python"
        assert "x = 1" in snippets[0].content
        assert snippets[0].line_number == 4

    def test_extracts_code_block_directive(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            # Title

            ```{code-block} yaml
            key: value
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 1
        assert snippets[0].language == "yaml"
        assert "key: value" in snippets[0].content

    def test_extracts_testcode_directive_as_python(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```{testcode}
            x = 42
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 1
        assert snippets[0].language == "python"
        assert "x = 42" in snippets[0].content

    def test_testcode_with_skipif_option_strips_option_line(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```{testcode}
            :skipif: True
            client.power.on()
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 1
        assert "skipif" not in snippets[0].content
        assert "client.power.on()" in snippets[0].content

    def test_skips_mermaid_blocks(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```{mermaid}
            graph TD
                A --> B
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 0

    def test_skips_toctree_blocks(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```{toctree}
            page1
            page2
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 0

    def test_skips_note_warning_tip_blocks(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```{note}
            This is a note.
            ```

            ```{warning}
            This is a warning.
            ```

            ```{tip}
            This is a tip.
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 0

    def test_multiple_snippets_in_one_file(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```python
            x = 1
            ```

            ```yaml
            key: value
            ```

            ```bash
            echo hello
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 3
        assert snippets[0].language == "python"
        assert snippets[1].language == "yaml"
        assert snippets[2].language == "bash"

    def test_skips_tab_wrapper_but_extracts_inner_blocks(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ````{tab} GitHub
            ```yaml
            jobs:
              test:
                runs-on: ubuntu-latest
            ```
            ````
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 1
        assert snippets[0].language == "yaml"

    def test_code_block_with_options_skips_option_lines(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```{code-block} yaml
            :substitutions:
            key: value
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 1
        assert "substitutions" not in snippets[0].content
        assert "key: value" in snippets[0].content

    def test_plain_fence_preserves_colon_prefixed_lines(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```yaml
            :key: value
            other: data
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 1
        assert ":key: value" in snippets[0].content

    def test_code_block_directive_strips_options(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```{code-block} python
            :linenos:
            x = 1
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 1
        assert "linenos" not in snippets[0].content
        assert "x = 1" in snippets[0].content

    def test_testcode_directive_strips_options(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```{testcode}
            :skipif: True
            x = 1
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 1
        assert "skipif" not in snippets[0].content
        assert "x = 1" in snippets[0].content

    def test_empty_code_block_is_skipped(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```python

            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert len(snippets) == 0

    def test_records_correct_file_path(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ```python
            x = 1
            ```
            """),
            encoding="utf-8",
        )
        snippets = extract_snippets(str(md))
        assert snippets[0].file_path == str(md)


class TestValidatePython:
    def test_valid_python_passes(self):
        snippet = Snippet("python", "x = 1\ny = x + 1\n", "test.md", 1)
        validate_python(snippet)

    def test_syntax_error_fails(self):
        snippet = Snippet("python", "def foo(\n", "test.md", 10)
        with pytest.raises(pytest.fail.Exception, match="Python syntax error"):
            validate_python(snippet)

    def test_missing_import_still_compiles(self):
        snippet = Snippet("python", "from nonexistent import thing\nx = thing()\n", "test.md", 1)
        validate_python(snippet)


class TestValidateYaml:
    def test_valid_yaml_passes(self):
        snippet = Snippet("yaml", "key: value\nlist:\n  - item1\n  - item2\n", "test.md", 1)
        validate_yaml(snippet)

    def test_invalid_yaml_fails(self):
        snippet = Snippet("yaml", "key: [\ninvalid\n", "test.md", 10)
        with pytest.raises(pytest.fail.Exception, match="YAML parse error"):
            validate_yaml(snippet)

    def test_myst_substitutions_are_replaced(self):
        snippet = Snippet("yaml", "image: quay.io/test:{{version}}\n", "test.md", 1)
        validate_yaml(snippet)

    def test_multi_document_yaml_passes(self):
        snippet = Snippet("yaml", "key: value\n---\nother: data\n", "test.md", 1)
        validate_yaml(snippet)


class TestValidateBash:
    def test_valid_bash_passes(self):
        snippet = Snippet("bash", "echo hello\nls -la\n", "test.md", 1)
        validate_bash(snippet)

    def test_invalid_bash_fails(self):
        snippet = Snippet("bash", "if then\n", "test.md", 10)
        with pytest.raises(pytest.fail.Exception, match="Bash syntax error"):
            validate_bash(snippet)

    def test_console_strips_prompt_markers(self):
        snippet = Snippet("console", "$ echo hello\noutput line\n$ ls\n", "test.md", 1)
        validate_bash(snippet)

    def test_console_ignores_output_lines(self):
        content = "$ echo hello\nhello\n$ echo world\nworld\n"
        commands = _extract_bash_commands(content)
        assert commands.strip().splitlines() == ["echo hello", "echo world"]

    def test_empty_commands_passes(self):
        snippet = Snippet("console", "some output only\n", "test.md", 1)
        validate_bash(snippet)

    def test_angle_bracket_placeholders_are_replaced(self):
        snippet = Snippet("console", "$ jmp login --client <alias>\n", "test.md", 1)
        validate_bash(snippet)

    def test_usage_output_is_skipped(self):
        content = "Usage: j storage flash [OPTIONS] [FILE]\n\n  Flash image(s) to DUT\n"
        snippet = Snippet("bash", content, "test.md", 1)
        validate_bash(snippet)

    def test_bash_with_comments_passes(self):
        snippet = Snippet("bash", "# This is a comment\necho hello\n", "test.md", 1)
        validate_bash(snippet)

    def test_continuation_lines_are_joined(self):
        content = "$ jmp login \\\n    --endpoint https://example.com\n"
        commands = _extract_bash_commands(content)
        assert "jmp login \\" in commands
        assert "--endpoint" in commands


class TestValidateBashTimeout:
    def test_timeout_raises_pytest_fail(self, monkeypatch):
        def mock_run(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd=["bash", "-n"], timeout=10)

        monkeypatch.setattr(subprocess, "run", mock_run)
        snippet = Snippet("bash", "echo hello\n", "test.md", 5)
        with pytest.raises(pytest.fail.Exception, match="timed out"):
            validate_bash(snippet)


class TestExtractBashCommands:
    def test_empty_input(self):
        assert _extract_bash_commands("") == ""

    def test_only_output_lines(self):
        content = "output line 1\noutput line 2\n"
        assert _extract_bash_commands(content) == ""

    def test_single_command(self):
        content = "$ echo hello\n"
        assert _extract_bash_commands(content) == "echo hello"

    def test_continuation_not_preceded_by_backslash(self):
        content = "$ echo hello\n    continuation without backslash\n"
        result = _extract_bash_commands(content)
        assert result == "echo hello"

    def test_multiple_commands_with_output(self):
        content = "$ echo a\noutput a\n$ echo b\noutput b\n"
        lines = _extract_bash_commands(content).splitlines()
        assert lines == ["echo a", "echo b"]


class TestReplaceMystSubstitutions:
    def test_single_substitution(self):
        result = _replace_myst_substitutions("image: {{version}}")
        assert result == "image: PLACEHOLDER_version"

    def test_multiple_substitutions(self):
        result = _replace_myst_substitutions("{{version}} and {{index_url}}")
        assert result == "PLACEHOLDER_version and PLACEHOLDER_index_url"

    def test_no_substitutions(self):
        result = _replace_myst_substitutions("plain text")
        assert result == "plain text"


class TestReplaceAngleBracketPlaceholders:
    def test_single_placeholder(self):
        result = _replace_angle_bracket_placeholders("--client <alias>")
        assert result == "--client PLACEHOLDER"

    def test_multiple_placeholders(self):
        result = _replace_angle_bracket_placeholders("<host>:<port>")
        assert result == "PLACEHOLDER:PLACEHOLDER"

    def test_no_placeholders(self):
        result = _replace_angle_bracket_placeholders("plain text")
        assert result == "plain text"


class TestLooksLikeUsageOutput:
    def test_usage_line_detected(self):
        assert _looks_like_usage_output("Usage: j storage flash [OPTIONS]")

    def test_normal_bash_not_detected(self):
        assert not _looks_like_usage_output("echo hello")

    def test_empty_content_not_detected(self):
        assert not _looks_like_usage_output("")


class TestValidatorsAndSyntaxCheckableConsistency:
    def test_syntax_checkable_matches_validators_keys(self):
        assert SYNTAX_CHECKABLE == frozenset(VALIDATORS.keys())

    def test_every_checkable_language_has_a_validator(self):
        for lang in SYNTAX_CHECKABLE:
            assert lang in VALIDATORS, f"Missing validator for {lang}"

    def test_shell_not_in_syntax_checkable(self):
        assert "shell" not in SYNTAX_CHECKABLE

    def test_shell_not_in_validators(self):
        assert "shell" not in VALIDATORS

    def test_no_snippet_language_is_shell_after_normalization(self):
        assert _normalize_language("shell") == "bash"
        assert _normalize_language("sh") == "bash"


class TestCollectAllSnippetsIsPublic:
    def testcollect_all_snippets_is_callable(self):
        assert callable(collect_all_snippets)

    def testcollect_all_snippets_returns_list(self, tmp_path, monkeypatch):
        md = tmp_path / "test.md"
        md.write_text("```python\nx = 1\n```\n", encoding="utf-8")
        monkeypatch.setattr("doc_snippet_test.DOCS_DIR", str(tmp_path))
        result = collect_all_snippets()
        assert isinstance(result, list)
        assert len(result) == 1


class TestSnippetId:
    def test_generates_readable_id(self):
        snippet = Snippet("python", "x = 1", "/docs/source/test.md", 42)
        sid = _snippet_id(snippet)
        assert "test.md" in sid
        assert "42" in sid
        assert "python" in sid


def _parametrize_snippets() -> list[pytest.ParameterSet]:
    snippets = _get_syntax_checkable_snippets()
    return [pytest.param(s, id=_snippet_id(s)) for s in snippets]


@pytest.mark.parametrize("snippet", _parametrize_snippets())
def test_doc_snippet(snippet: Snippet):
    VALIDATORS[snippet.language](snippet)
