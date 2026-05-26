from __future__ import annotations

import subprocess
import textwrap

import pytest
from doc_snippet import (
    SKIP_DIRECTIVES,
    SYNTAX_CHECKABLE,
    VALIDATORS,
    FenceOpening,
    Snippet,
    _extract_bash_commands,
    _is_skip_directive,
    _looks_like_usage_output,
    _normalize_language,
    _parse_fence_opening,
    _read_block_content,
    _replace_angle_bracket_placeholders,
    _replace_myst_substitutions,
    _skip_option_lines,
    _snippet_id,
    collect_all_snippets,
    extract_snippets,
    validate_bash,
    validate_python,
    validate_yaml,
)


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

    def test_longer_backtick_line_does_not_close_shorter_fence(self):
        lines = ["line 1\n", "````\n", "line 2\n", "```\n"]
        content, end = _read_block_content(lines, 0, "```")
        assert content == "line 1\n````\nline 2\n"
        assert end == 3


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


class _FakeTerminalReporter:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.sections: list[str] = []

    def section(self, title: str) -> None:
        self.sections.append(title)

    def write_line(self, line: str) -> None:
        self.lines.append(line)


class TestPytestTerminalSummary:
    def test_reports_section_title(self, tmp_path, monkeypatch):
        md = tmp_path / "test.md"
        md.write_text("```python\nx = 1\n```\n", encoding="utf-8")
        monkeypatch.setattr("doc_snippet.DOCS_DIR", str(tmp_path))

        import conftest

        reporter = _FakeTerminalReporter()
        conftest.pytest_terminal_summary(reporter, 0, None)
        assert reporter.sections == ["Documentation Snippet Coverage"]

    def test_reports_language_counts(self, tmp_path, monkeypatch):
        md = tmp_path / "test.md"
        md.write_text("```python\nx = 1\n```\n\n```yaml\nkey: val\n```\n\n```json\n{}\n```\n", encoding="utf-8")
        monkeypatch.setattr("doc_snippet.DOCS_DIR", str(tmp_path))

        import conftest

        reporter = _FakeTerminalReporter()
        conftest.pytest_terminal_summary(reporter, 0, None)
        python_line = [line for line in reporter.lines if "python:" in line]
        assert len(python_line) == 1
        assert "1/1" in python_line[0]
        assert "[tested]" in python_line[0]

        json_line = [line for line in reporter.lines if "json:" in line]
        assert len(json_line) == 1
        assert "0/1" in json_line[0]
        assert "[recognized]" in json_line[0]

    def test_reports_total_summary(self, tmp_path, monkeypatch):
        md = tmp_path / "test.md"
        md.write_text("```python\nx = 1\n```\n\n```json\n{}\n```\n", encoding="utf-8")
        monkeypatch.setattr("doc_snippet.DOCS_DIR", str(tmp_path))

        import conftest

        reporter = _FakeTerminalReporter()
        conftest.pytest_terminal_summary(reporter, 0, None)
        total_lines = [line for line in reporter.lines if "Total:" in line]
        assert len(total_lines) == 1
        assert "1/2" in total_lines[0]

    def test_empty_docs_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr("doc_snippet.DOCS_DIR", str(tmp_path))

        import conftest

        reporter = _FakeTerminalReporter()
        conftest.pytest_terminal_summary(reporter, 0, None)
        total_lines = [line for line in reporter.lines if "Total:" in line]
        assert len(total_lines) == 1
        assert "0/0" in total_lines[0]


class TestConftestTypeAnnotations:
    def test_pytest_terminal_summary_has_return_annotation(self):
        import inspect

        import conftest

        sig = inspect.signature(conftest.pytest_terminal_summary)
        assert sig.return_annotation is not inspect.Parameter.empty

    def test_pytest_terminal_summary_has_parameter_annotations(self):
        import inspect

        import conftest

        sig = inspect.signature(conftest.pytest_terminal_summary)
        for name in ("terminalreporter", "exitstatus", "config"):
            param = sig.parameters[name]
            assert param.annotation is not inspect.Parameter.empty, f"Missing annotation for {name}"


class TestCollectAllSnippetsIsPublic:
    def test_collect_all_snippets_is_callable(self):
        assert callable(collect_all_snippets)

    def test_collect_all_snippets_returns_list(self, tmp_path, monkeypatch):
        md = tmp_path / "test.md"
        md.write_text("```python\nx = 1\n```\n", encoding="utf-8")
        monkeypatch.setattr("doc_snippet.DOCS_DIR", str(tmp_path))
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
