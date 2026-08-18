"""Explicit, root-only compatibility transforms for JSON-LD input."""

from __future__ import annotations

from typing import Any


def normalize_jsonld_context(data: dict[str, Any]) -> dict[str, Any]:
    """Flatten configured dict-context prefixes at the document root.

    This is intentionally lossy: a dict ``@context`` is removed after known
    prefixed root keys are flattened. String, list, malformed, and unknown
    contexts are retained. Nested dictionaries are never inspected.
    """

    context = data.get("@context")
    if not isinstance(context, dict):
        return dict(data)

    result = dict(data)
    configured_prefixes = tuple(key for key in context if isinstance(key, str))
    for key in tuple(data):
        if not isinstance(key, str):
            continue
        for prefix in configured_prefixes:
            marker = f"{prefix}:"
            if key.startswith(marker):
                target = key[len(marker) :]
                if target in data or target in result:
                    raise ValueError(
                        f"JSON-LD context normalization collision for {target!r}"
                    )
                result[target] = result.pop(key)
                break
    result.pop("@context", None)
    return result


def migrate_legacy_codemeta(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate the three legacy root-level CodeMeta property names.

    Migration is shallow and checks key presence rather than truthiness, so
    falsey values are migrated and simultaneous old/new keys are rejected.
    """

    result = dict(data)
    migrations = (
        ("embargoDate", "embargoEndDate"),
        ("contIntegration", "continuousIntegration"),
        ("creator", "author"),
    )
    for old, new in migrations:
        if old in data and new in data:
            raise ValueError(f"Cannot migrate {old!r}: {new!r} is also present")
        if old in data:
            result[new] = result.pop(old)
    return result
