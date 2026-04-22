from __future__ import annotations

import base64
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd


def _remote_cache_root() -> str:
    return os.getenv("PERSISTENT_CACHE_URI", "").strip().rstrip("/")


def remote_cache_enabled() -> bool:
    return bool(_remote_cache_root())


def _remote_cache_namespace() -> str:
    namespace = os.getenv("PERSISTENT_CACHE_NAMESPACE", "").strip().strip("/")
    return namespace or "shared"


def build_cache_target(
    *,
    filename: str,
    local_dir: Path,
    local_subdir: str | None = None,
) -> str | Path:
    remote_root = _remote_cache_root()
    if remote_root:
        namespace = _remote_cache_namespace()
        return f"{remote_root}/{namespace}/{filename}"

    target_dir = local_dir / local_subdir if local_subdir else local_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / filename


def target_exists(target: str | Path) -> bool:
    if _is_remote_target(target):
        return _remote_fs(target).exists(str(target))
    return Path(target).exists()


def remove_target(target: str | Path):
    try:
        if _is_remote_target(target):
            fs = _remote_fs(target)
            target_str = str(target)
            if fs.exists(target_str):
                fs.rm(target_str)
            return
        path = Path(target)
        if path.exists():
            path.unlink()
    except Exception:
        pass


def read_text(target: str | Path, encoding: str = "utf-8") -> str:
    if not target_exists(target):
        return ""
    if _is_remote_target(target):
        with _remote_fs(target).open(str(target), "r", encoding=encoding) as handle:
            return handle.read()
    return Path(target).read_text(encoding=encoding)


def write_text(target: str | Path, content: str, encoding: str = "utf-8"):
    if _is_remote_target(target):
        with _remote_fs(target).open(str(target), "w", encoding=encoding) as handle:
            handle.write(content)
        return
    path = Path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)


def read_json(target: str | Path) -> dict[str, Any]:
    raw = read_text(target)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def write_json(target: str | Path, payload: dict[str, Any]):
    write_text(target, json.dumps(payload, indent=2), encoding="utf-8")


def read_parquet(target: str | Path) -> pd.DataFrame:
    if not target_exists(target):
        return pd.DataFrame()
    try:
        if _is_remote_target(target):
            with _remote_fs(target).open(str(target), "rb") as handle:
                return pd.read_parquet(handle)
        return pd.read_parquet(target)
    except Exception:
        return pd.DataFrame()


def write_parquet(df: pd.DataFrame, target: str | Path, *, index: bool = False):
    if _is_remote_target(target):
        with _remote_fs(target).open(str(target), "wb") as handle:
            df.to_parquet(handle, index=index)
        return
    path = Path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=index)


def _is_remote_target(target: str | Path) -> bool:
    return isinstance(target, str) and "://" in target


def _remote_fs(target: str | Path):
    target_str = str(target)
    if target_str.startswith("gs://"):
        return _get_gcs_filesystem()
    raise ValueError(f"Unsupported persistent cache target: {target_str}")


@lru_cache(maxsize=1)
def _get_gcs_filesystem():
    try:
        import gcsfs
    except ImportError as exc:
        raise RuntimeError(
            "Persistent GCS cache requires `gcsfs`. Add it to requirements.txt."
        ) from exc

    kwargs: dict[str, Any] = {}
    project = (
        os.getenv("GCP_PROJECT")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCLOUD_PROJECT")
    )
    if project:
        kwargs["project"] = project

    token = _load_gcs_token()
    if token is not None:
        kwargs["token"] = token

    return gcsfs.GCSFileSystem(**kwargs)


def _load_gcs_token() -> Any | None:
    raw_json = (
        os.getenv("GCS_SERVICE_ACCOUNT_JSON")
        or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        or ""
    ).strip()
    if raw_json:
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError:
            return raw_json

    encoded = (
        os.getenv("GCS_SERVICE_ACCOUNT_JSON_B64")
        or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_B64")
        or ""
    ).strip()
    if encoded:
        try:
            return json.loads(base64.b64decode(encoded).decode("utf-8"))
        except Exception:
            return None

    key_path = (
        os.getenv("GCS_SERVICE_ACCOUNT_FILE")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        or ""
    ).strip()
    return key_path or None
