#!/usr/bin/env python3
"""Shared character-offset word tokenizer for OVERRIDE D5 models.

Guarantees: every token carries exact [start, end) char offsets into the
unmodified utterance; tokens never overlap; offsets are stable across CRF and
Transformer pipelines (same word layer, model subtokens align to words).

Token pattern: words (unicode letters/digits/underscore) or single non-space,
non-word characters. This makes multi-word gold spans align on token
boundaries in normal English text.
"""
from __future__ import annotations

import re
from typing import NamedTuple

TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


class Token(NamedTuple):
    start: int
    end: int
    text: str


def tokenize(text: str) -> list[Token]:
    return [Token(m.start(), m.end(), m.group()) for m in TOKEN_RE.finditer(text)]


def span_tokens(tokens: list[Token], start: int, end: int) -> list[int]:
    """Indices of tokens fully inside [start, end)."""
    return [i for i, t in enumerate(tokens) if t.start >= start and t.end <= end]


def partial_overlap(tokens: list[Token], start: int, end: int) -> bool:
    """True if some token straddles the span boundary (bad for token models)."""
    for t in tokens:
        if t.end > start and t.start < end and not (t.start >= start and t.end <= end):
            return True
    return False
