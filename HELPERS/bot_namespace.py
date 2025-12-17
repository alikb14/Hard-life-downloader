from __future__ import annotations

from typing import List

from CONFIG.config import Config, get_bot_namespace as config_get_bot_namespace


def get_bot_namespace() -> str:
    """
    Returns the configured bot namespace or raises if it is missing/empty.
    This is the single source of truth for database/cache/log namespaces.
    """
    return config_get_bot_namespace()


def ensure_bot_namespace() -> str:
    """
    Defensive guard to be called at startup to ensure the namespace is configured.
    Returns the validated namespace for convenience.
    """
    return get_bot_namespace()


def _split_raw_parts(raw_parts: List[str]) -> List[str]:
    cleaned: List[str] = []
    for part in raw_parts:
        if part is None:
            continue
        cleaned.extend([p for p in str(part).split("/") if p])
    return cleaned


def config_path_parts(path: str) -> List[str]:
    """
    Splits a config path and enforces the bot namespace as the second segment under 'bot'.
    Example:
      - "bot/video_cache" -> ["bot", <namespace>, "video_cache"]
      - "video_cache/playlists" -> ["bot", <namespace>, "video_cache", "playlists"]
    """
    namespace = get_bot_namespace()
    raw_parts = _split_raw_parts([path])
    if raw_parts[:1] == ["bot"]:
        # Force namespace into second position (replace legacy values)
        tail = raw_parts[2:] if len(raw_parts) > 2 else []
        raw_parts = ["bot", namespace] + tail if len(raw_parts) > 1 else ["bot", namespace]
    else:
        raw_parts = ["bot", namespace] + raw_parts
    return raw_parts


def namespaced_path(*parts: str) -> str:
    """Builds a namespaced path string starting with bot/<namespace>/..."""
    return "/".join(config_path_parts("/".join(_split_raw_parts(list(parts)))))
