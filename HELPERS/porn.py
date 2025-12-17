"""
NSFW/porn detection stubs.

This project no longer performs any porn/NSFW checks. All helpers return
non‑NSFW results and the reload logic simply returns empty counts so the rest
of the code can keep working without conditionals.
"""

from urllib.parse import urlparse

from CONFIG.messages import safe_get_messages
from HELPERS.logger import logger

# Exposed sets for imports in other modules
PORN_DOMAINS = set()
PORN_KEYWORDS = set()
SUPPORTED_SITES = set()


def unwrap_redirect_url(url: str) -> str:
    """Return URL as-is (stub)."""
    return url


def extract_domain_parts(url: str):
    """
    Minimal domain extraction stub.
    Returns ([domain], domain) or ([], '') on failure.
    """
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if host:
            return [host], host
    except Exception:
        pass
    return [], ""


def is_porn_domain(domain_parts):
    """Always treat domains as non‑NSFW."""
    return False


def is_porn(url: str, title: str, description: str, caption=None, tags=None) -> bool:
    """Always treat content as non‑NSFW."""
    return False


def check_porn_detailed(url: str, title: str, description: str, caption=None):
    """
    Always return (False, explanation) to indicate NSFW checks are disabled.
    """
    messages = safe_get_messages(None)
    explanation = getattr(messages, "PORN_NO_KEYWORDS_FOUND_MSG", "NSFW checking disabled")
    return False, explanation


def reload_all_porn_caches():
    """
    No-op reload. Returns empty counters for compatibility with admin command.
    """
    logger.info("[NSFW] Porn/NSFW detection disabled; reload is a no-op")
    return {
        "porn_domains": 0,
        "porn_keywords": 0,
        "supported_sites": 0,
        "whitelist": 0,
        "greylist": 0,
        "black_list": 0,
        "white_keywords": 0,
        "proxy_domains": 0,
        "proxy_2_domains": 0,
        "clean_query": 0,
        "no_cookie_domains": 0,
    }
