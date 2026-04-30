import importlib
import re
from pathlib import Path

import pytest

DOCS_SOURCE_DIR = Path(__file__).parent / "source"

JUMPSTARTER_IMPORT_PATTERN = re.compile(
    r"^\s*from\s+(jumpstarter\S*)\s+import\s+(.+)$"
)

JUMPSTARTER_BARE_IMPORT_PATTERN = re.compile(
    r"^\s*import\s+(jumpstarter\S*)$"
)


def _extract_python_code_blocks(md_path: Path) -> list[tuple[int, str]]:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    blocks: list[tuple[int, str]] = []
    in_python_block = False
    block_start = 0
    block_lines: list[str] = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not in_python_block and (
            stripped.startswith("```python") or stripped.startswith("```{testcode}")
        ):
            in_python_block = True
            block_start = i + 1
            block_lines = []
        elif in_python_block and stripped == "```":
            in_python_block = False
            blocks.append((block_start, "\n".join(block_lines)))
        elif in_python_block:
            block_lines.append(line)

    return blocks


def _extract_jumpstarter_imports(
    md_path: Path,
) -> list[tuple[int, str, list[str]]]:
    results: list[tuple[int, str, list[str]]] = []
    blocks = _extract_python_code_blocks(md_path)

    for block_start, block_content in blocks:
        for offset, line in enumerate(block_content.splitlines()):
            line_without_comment = line.split("#")[0]
            from_match = JUMPSTARTER_IMPORT_PATTERN.match(
                line_without_comment
            )
            if from_match:
                module_path = from_match.group(1)
                names = [
                    n.strip().split()[0]
                    for n in from_match.group(2).split(",")
                    if n.strip()
                ]
                line_number = block_start + offset + 1
                results.append((line_number, module_path, names))
                continue

            bare_match = JUMPSTARTER_BARE_IMPORT_PATTERN.match(line)
            if bare_match:
                module_path = bare_match.group(1)
                line_number = block_start + offset + 1
                results.append((line_number, module_path, []))

    return results


def _find_all_doc_markdown_files() -> list[Path]:
    if not DOCS_SOURCE_DIR.exists():
        return []
    return sorted(DOCS_SOURCE_DIR.rglob("*.md"))


def _collect_all_imports() -> (
    list[tuple[Path, int, str, list[str]]]
):
    all_imports: list[tuple[Path, int, str, list[str]]] = []
    for md_file in _find_all_doc_markdown_files():
        imports = _extract_jumpstarter_imports(md_file)
        for line_num, module_path, names in imports:
            all_imports.append((md_file, line_num, module_path, names))
    return all_imports


def _import_id(item: tuple[Path, int, str, list[str]]) -> str:
    md_file, line_num, module_path, names = item
    relative = md_file.relative_to(DOCS_SOURCE_DIR)
    if names:
        return f"{relative}:{line_num} from {module_path} import {', '.join(names)}"
    return f"{relative}:{line_num} import {module_path}"


def _lazy_collect_all_imports() -> list[tuple[Path, int, str, list[str]]]:
    if not hasattr(_lazy_collect_all_imports, "_cached"):
        _lazy_collect_all_imports._cached = _collect_all_imports()
    return _lazy_collect_all_imports._cached


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "import_entry" in metafunc.fixturenames:
        all_imports = _lazy_collect_all_imports()
        metafunc.parametrize(
            "import_entry",
            all_imports,
            ids=_import_id,
        )


def test_documented_import_is_resolvable(
    import_entry: tuple[Path, int, str, list[str]],
) -> None:
    md_file, line_num, module_path, names = import_entry
    relative_path = md_file.relative_to(DOCS_SOURCE_DIR)

    try:
        mod = importlib.import_module(module_path)
    except ImportError as exc:
        pytest.fail(
            f"{relative_path}:{line_num} - "
            f"cannot import module '{module_path}': {exc}"
        )

    for name in names:
        if not hasattr(mod, name):
            pytest.fail(
                f"{relative_path}:{line_num} - "
                f"module '{module_path}' has no attribute '{name}'"
            )


def test_import_parsing_strips_as_alias(tmp_path: Path) -> None:
    md_file = tmp_path / "alias.md"
    md_file.write_text(
        "```python\n"
        "from jumpstarter.common.utils import env as environment\n"
        "```\n",
        encoding="utf-8",
    )
    imports = _extract_jumpstarter_imports(md_file)
    assert len(imports) == 1
    _, _, names = imports[0]
    assert names == ["env"], (
        f"Expected ['env'] after stripping alias, got {names}"
    )


def test_import_parsing_strips_inline_comment(tmp_path: Path) -> None:
    md_file = tmp_path / "comment.md"
    md_file.write_text(
        "```python\n"
        "from jumpstarter.common.utils import env  # utility\n"
        "```\n",
        encoding="utf-8",
    )
    imports = _extract_jumpstarter_imports(md_file)
    assert len(imports) == 1
    _, _, names = imports[0]
    assert names == ["env"], (
        f"Expected ['env'] after stripping comment, got {names}"
    )


def test_jumpstarter_test_uses_selector_not_exporter_selector() -> None:
    from jumpstarter_testing.pytest import JumpstarterTest

    annotations = getattr(JumpstarterTest, "__annotations__", {})
    has_selector = (
        "selector" in annotations or hasattr(JumpstarterTest, "selector")
    )
    has_exporter_selector = (
        "exporter_selector" in annotations
        or hasattr(JumpstarterTest, "exporter_selector")
    )

    assert has_selector, (
        "JumpstarterTest should have a 'selector' class variable "
        "but it was not found in annotations or attributes"
    )
    assert not has_exporter_selector, (
        "JumpstarterTest has 'exporter_selector' which is not the "
        "correct attribute name; it should be 'selector'"
    )


def test_jumpstarter_test_client_is_fixture_method() -> None:
    from jumpstarter_testing.pytest import JumpstarterTest

    client_attr = getattr(JumpstarterTest, "client", None)
    assert client_attr is not None, (
        "JumpstarterTest should have a 'client' method (pytest fixture)"
    )
    assert callable(client_attr), (
        "JumpstarterTest.client should be callable (a pytest fixture method), "
        "not a plain attribute"
    )


def test_docs_do_not_use_exporter_selector() -> None:
    integration_patterns = (
        DOCS_SOURCE_DIR
        / "getting-started"
        / "guides"
        / "integration-patterns.md"
    )
    if not integration_patterns.exists():
        pytest.skip("integration-patterns.md not found")

    content = integration_patterns.read_text(encoding="utf-8")
    lines_with_exporter_selector = [
        (i + 1, line)
        for i, line in enumerate(content.splitlines())
        if "exporter_selector" in line
    ]
    assert not lines_with_exporter_selector, (
        "integration-patterns.md uses 'exporter_selector' instead of "
        "'selector'. Found at lines: "
        + ", ".join(
            f"{ln}: {text.strip()}"
            for ln, text in lines_with_exporter_selector
        )
    )


def test_docs_do_not_use_self_client_pattern() -> None:
    integration_patterns = (
        DOCS_SOURCE_DIR
        / "getting-started"
        / "guides"
        / "integration-patterns.md"
    )
    if not integration_patterns.exists():
        pytest.skip("integration-patterns.md not found")

    content = integration_patterns.read_text(encoding="utf-8")

    self_client_pattern = re.compile(r"self\.client\.")
    lines_with_pattern: list[tuple[int, str]] = []

    in_python_block = False
    for i, line in enumerate(content.splitlines()):
        stripped = line.strip()
        if stripped.startswith("```python") or stripped.startswith("```{testcode}"):
            in_python_block = True
            continue
        if stripped == "```":
            in_python_block = False
            continue
        if in_python_block and self_client_pattern.search(line):
            lines_with_pattern.append((i + 1, line))

    assert not lines_with_pattern, (
        "integration-patterns.md uses 'self.client' pattern in Python code "
        "blocks instead of the 'client' fixture parameter. Found at lines: "
        + ", ".join(
            f"{ln}: {text.strip()}" for ln, text in lines_with_pattern
        )
    )
