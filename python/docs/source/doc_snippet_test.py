from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from doc_snippet import VALIDATORS, Snippet, _get_syntax_checkable_snippets, _snippet_id

if TYPE_CHECKING:
    from _pytest.mark.structures import ParameterSet


def _parametrize_snippets() -> list[ParameterSet]:
    snippets = _get_syntax_checkable_snippets()
    return [pytest.param(s, id=_snippet_id(s)) for s in snippets]


@pytest.mark.parametrize("snippet", _parametrize_snippets())
def test_doc_snippet(snippet: Snippet):
    VALIDATORS[snippet.language](snippet)
