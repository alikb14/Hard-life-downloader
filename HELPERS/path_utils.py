import os
import re
from urllib.parse import urlparse

import tldextract


def _sanitize_path_component(value: str, fallback: str = "unknown") -> str:
    """Return a filesystem-safe component (alnum, dot, underscore, dash)."""
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", (value or "").strip())
    safe = safe.strip("._-")
    return safe or fallback


def detect_platform_from_url(url: str | None, default: str = "unknown") -> str:
    """
    Best-effort platform name from a URL; falls back to sanitized registrable domain.
    Examples: youtube.com/youtu.be -> youtube, drive.google.com -> google-drive.
    """
    if not url:
        return default

    try:
        url = url.strip()
        lower_url = url.lower()
        parsed = urlparse(url)

        known_map = {
            "youtube": ("youtube.com", "youtu.be", "ytimg.com"),
            "instagram": ("instagram.com", "instagr.am"),
            "facebook": ("facebook.com", "fb.watch", "fb.com", "m.facebook.com"),
            "tiktok": ("tiktok.com",),
            "twitter": ("twitter.com", "x.com"),
            "telegram": ("t.me", "telegram.me"),
            "google-drive": ("drive.google.com", "docs.google.com"),
        }
        for name, needles in known_map.items():
            if any(needle in lower_url for needle in needles):
                return _sanitize_path_component(name, default)

        ext = tldextract.extract(url)
        candidate = ext.domain or parsed.netloc.split(":")[0]

        # Fix a few common shorthand domains
        if candidate == "youtu":
            candidate = "youtube"
        elif candidate == "fb":
            candidate = "facebook"
        elif candidate == "google":
            if "drive" in parsed.path.lower() or "docs" in parsed.path.lower():
                candidate = "google-drive"

        return _sanitize_path_component(candidate, default)
    except Exception:
        return default


def build_local_save_paths(
    base_dir: str,
    platform: str,
    user_folder: str,
    share_base: str | None = None,
) -> tuple[str, str]:
    """Return (dest_dir, display_dir) for user/platform inside the base dir."""
    dest_dir = os.path.join(base_dir, user_folder, platform)
    display_dir = dest_dir if not share_base else os.path.join(share_base, user_folder, platform)
    return dest_dir, display_dir
