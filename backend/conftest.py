import importlib.metadata

# Defensive patch for broken package metadata in local environment
_orig_version = importlib.metadata.version


def _safe_version(distribution_name: str) -> str:
    try:
        ver = _orig_version(distribution_name)
        if ver:
            return ver
    except Exception:
        pass
    return "2.0.0"


importlib.metadata.version = _safe_version
