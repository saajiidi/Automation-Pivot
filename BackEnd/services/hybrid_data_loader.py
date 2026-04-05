"""Hybrid data loader - combines historical parquet with live sheets and WooCommerce data."""

from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO
import json
import os
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
import streamlit as st

from BackEnd.services.woocommerce_service import get_woocommerce_credentials
from BackEnd.utils.sales_schema import ensure_sales_schema
from FrontEnd.utils.error_handler import log_error

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "data.parquet"
LOCAL_CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache" / "local_users"
LIVE_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTOiRkybNzMNvEaLxSFsX0nGIiM07BbNVsBbsX1dG8AmGOmSu8baPrVYL0cOqoYN4tRWUj1UjUbH1Ij/pub?gid=2118542421&single=true&output=csv"
LIVE_STREAM_URL = "https://docs.google.com/spreadsheets/d/1QQX4gDIEurTDkiyXcK1SO2-oYNqarhEg1fqRCVHspQw/export?format=csv&gid=2118542421"
COMPARISON_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTOiRkybNzMNvEaLxSFsX0nGIiM07BbNVsBbsX1dG8AmGOmSu8baPrVYL0cOqoYN4tRWUj1UjUbH1Ij/pub?gid=2136999354&single=true&output=csv"
WOO_CACHE_TTL_MINUTES = 360
STOCK_CACHE_TTL_MINUTES = 20


def _local_user_slug() -> str:
    raw = (
        os.getenv("USERNAME")
        or os.getenv("USER")
        or os.getenv("COMPUTERNAME")
        or "default_user"
    )
    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in raw).strip("_")
    return slug or "default_user"


def _user_cache_dir() -> Path:
    path = LOCAL_CACHE_DIR / _local_user_slug()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_file(name: str) -> Path:
    return _user_cache_dir() / name


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


def _is_fresh(timestamp: str | None, ttl_minutes: int) -> bool:
    if not timestamp:
        return False
    parsed = pd.to_datetime(timestamp, errors="coerce")
    if pd.isna(parsed):
        return False
    age = datetime.now() - parsed.to_pydatetime()
    return age <= timedelta(minutes=ttl_minutes)


def _normalize_bounds(start_date: Optional[str], end_date: Optional[str], days: int) -> tuple[pd.Timestamp, pd.Timestamp]:
    start_ts = (
        pd.to_datetime(start_date, errors="coerce")
        if start_date
        else pd.Timestamp.now().normalize() - pd.Timedelta(days=days)
    )
    end_ts = pd.to_datetime(end_date, errors="coerce") if end_date else pd.Timestamp.now()
    if pd.isna(start_ts):
        start_ts = pd.Timestamp.now().normalize() - pd.Timedelta(days=days)
    if pd.isna(end_ts):
        end_ts = pd.Timestamp.now()
    return start_ts.normalize(), end_ts.normalize() + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)


def _filter_by_date_range(df: pd.DataFrame, start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> pd.DataFrame:
    if df.empty or "order_date" not in df.columns:
        return df
    filtered = df.copy()
    filtered["order_date"] = pd.to_datetime(filtered["order_date"], errors="coerce")
    filtered = filtered[filtered["order_date"].between(start_ts, end_ts, inclusive="both")]
    return filtered.reset_index(drop=True)


def estimate_woocommerce_load_time(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    start_ts, end_ts = _normalize_bounds(start_date, end_date, days=30)
    meta = _read_json(_cache_file("woo_orders_meta.json"))
    cached_start = pd.to_datetime(meta.get("cached_start"), errors="coerce")
    cached_end = pd.to_datetime(meta.get("cached_end"), errors="coerce")
    if (
        not pd.isna(cached_start)
        and not pd.isna(cached_end)
        and cached_start <= start_ts
        and cached_end >= end_ts
        and _is_fresh(meta.get("fetched_at"), WOO_CACHE_TTL_MINUTES)
    ):
        return "Estimated load time: 1-3 seconds from local cache."
    return "Estimated load time: 15-60 seconds if WooCommerce refresh is needed."


@st.cache_data(ttl=900)
def load_woocommerce_live_data(
    days: int = 30,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    if not get_woocommerce_credentials():
        return pd.DataFrame()

    try:
        from BackEnd.services.woocommerce_service import WooCommerceService

        start_ts, end_ts = _normalize_bounds(start_date, end_date, days)
        cache_path = _cache_file("woo_orders.parquet")
        meta_path = _cache_file("woo_orders_meta.json")
        cached_df = ensure_sales_schema(_read_parquet(cache_path))
        meta = _read_json(meta_path)
        cached_start = pd.to_datetime(meta.get("cached_start"), errors="coerce")
        cached_end = pd.to_datetime(meta.get("cached_end"), errors="coerce")

        if (
            not cached_df.empty
            and not pd.isna(cached_start)
            and not pd.isna(cached_end)
            and cached_start <= start_ts
            and cached_end >= end_ts
            and _is_fresh(meta.get("fetched_at"), WOO_CACHE_TTL_MINUTES)
        ):
            return _filter_by_date_range(cached_df, start_ts, end_ts)

        wc_service = WooCommerceService()
        after = start_ts.strftime("%Y-%m-%dT00:00:00Z")
        before = end_ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        fetched_df = wc_service.fetch_all_historical_orders(after=after, before=before, status="any")
        if fetched_df.empty:
            return _filter_by_date_range(cached_df, start_ts, end_ts) if not cached_df.empty else fetched_df

        fetched_df["_source"] = fetched_df.get("_source", "woocommerce_live")
        fetched_df = ensure_sales_schema(fetched_df)

        merged_cache = fetched_df if cached_df.empty else ensure_sales_schema(
            pd.concat([cached_df, fetched_df], ignore_index=True, sort=False)
        )
        merged_cache = _dedupe_orders(merged_cache)
        merged_cache.to_parquet(cache_path, index=False)

        new_cached_start = min(start_ts, cached_start) if not pd.isna(cached_start) else start_ts
        new_cached_end = max(end_ts, cached_end) if not pd.isna(cached_end) else end_ts
        _write_json(
            meta_path,
            {
                "cached_start": new_cached_start.strftime("%Y-%m-%d %H:%M:%S"),
                "cached_end": new_cached_end.strftime("%Y-%m-%d %H:%M:%S"),
                "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": _local_user_slug(),
            },
        )

        return _filter_by_date_range(merged_cache, start_ts, end_ts)
    except Exception as exc:
        log_error(
            exc,
            context="Hybrid Loader - WooCommerce Live",
            details={"days": days, "start_date": start_date, "end_date": end_date},
        )
        return pd.DataFrame()


@st.cache_data(ttl=900)
def load_woocommerce_stock_data() -> pd.DataFrame:
    """Fetch live stock directly from the WooCommerce REST API."""
    if not get_woocommerce_credentials():
        return pd.DataFrame()

    try:
        from BackEnd.services.woocommerce_service import WooCommerceService

        cache_path = _cache_file("woo_stock.parquet")
        meta_path = _cache_file("woo_stock_meta.json")
        cached_df = _read_parquet(cache_path)
        meta = _read_json(meta_path)
        if not cached_df.empty and _is_fresh(meta.get("fetched_at"), STOCK_CACHE_TTL_MINUTES):
            return cached_df

        wc_service = WooCommerceService()
        df = wc_service.get_stock_report()
        if df.empty:
            return cached_df if not cached_df.empty else df

        stock_df = df.copy()
        if "Stock Quantity" in stock_df.columns:
            stock_df["Stock Quantity"] = pd.to_numeric(stock_df["Stock Quantity"], errors="coerce").fillna(0)
        if "Price" in stock_df.columns:
            stock_df["Price"] = pd.to_numeric(stock_df["Price"], errors="coerce").fillna(0.0)
        stock_df["_source"] = "woocommerce_stock_api"
        stock_df["_imported_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stock_df.to_parquet(cache_path, index=False)
        _write_json(
            meta_path,
            {
                "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": _local_user_slug(),
                "rows": int(len(stock_df)),
            },
        )
        return stock_df
    except Exception as exc:
        log_error(exc, context="Hybrid Loader - WooCommerce Stock")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_live_2026_data() -> pd.DataFrame:
    try:
        response = requests.get(LIVE_SHEET_URL, timeout=60)
        response.raise_for_status()
        df = pd.read_csv(BytesIO(response.content))
        if df.empty:
            return df
        df["year"] = df.get("year", "2026")
        df["_source"] = df.get("_source", "live_gsheet")
        df["_imported_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return ensure_sales_schema(df)
    except Exception as exc:
        log_error(exc, context="Hybrid Loader - Google Sheet Live", details={"url": LIVE_SHEET_URL})
        return pd.DataFrame()


@st.cache_data(ttl=900)
def load_live_stream_data() -> pd.DataFrame:
    """Load exclusive Live Stream data."""
    try:
        response = requests.get(LIVE_STREAM_URL, timeout=60)
        response.raise_for_status()
        df = pd.read_csv(BytesIO(response.content))
        if df.empty:
            return df
        df["_source"] = "live_stream_gsheet"
        df["_imported_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return ensure_sales_schema(df)
    except Exception as exc:
        log_error(exc, context="Hybrid Loader - Live Stream", details={"url": LIVE_STREAM_URL})
        return pd.DataFrame()


@st.cache_data(ttl=900)
def load_comparison_data() -> pd.DataFrame:
    """Load Comparison data for Today vs Last Day analysis."""
    try:
        response = requests.get(COMPARISON_SHEET_URL, timeout=60)
        response.raise_for_status()
        df = pd.read_csv(BytesIO(response.content))
        if df.empty:
            return df
        df["_source"] = "comparison_gsheet"
        return ensure_sales_schema(df)
    except Exception as exc:
        log_error(exc, context="Hybrid Loader - Comparison Sheet", details={"url": COMPARISON_SHEET_URL})
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_historical_data() -> pd.DataFrame:
    data_dir = DATA_FILE.parent
    parquet_files = list(data_dir.glob("*.parquet"))
    partitioned_files = list(data_dir.glob("year=*/*.parquet"))
    if not parquet_files and not partitioned_files:
        return pd.DataFrame()

    frames: list[pd.DataFrame] = []
    for path in parquet_files + partitioned_files:
        try:
            frame = pd.read_parquet(path)
            if frame.empty:
                continue
            if "year" not in frame.columns and "year=" in str(path.parent.name):
                try:
                    frame["year"] = int(path.parent.name.replace("year=", ""))
                except ValueError:
                    pass
            frames.append(frame)
        except Exception as exc:
            log_error(exc, context="Hybrid Loader - Historical Parquet", details={"path": str(path)})

    if not frames:
        return pd.DataFrame()

    return ensure_sales_schema(pd.concat(frames, ignore_index=True, sort=False))


def _dedupe_orders(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "order_item_key" not in df.columns:
        return df
    return df.drop_duplicates(subset=["order_item_key", "source"], keep="last")


def load_hybrid_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_gsheet: bool = True,
    include_woocommerce: bool = True,
) -> pd.DataFrame:
    df_hist = load_historical_data()
    df_gsheet = load_live_2026_data() if include_gsheet else pd.DataFrame()
    df_woo = (
        load_woocommerce_live_data(start_date=start_date, end_date=end_date)
        if include_woocommerce
        else pd.DataFrame()
    )

    frames = [df for df in [df_hist, df_gsheet, df_woo] if df is not None and not df.empty]
    if not frames:
        return pd.DataFrame()

    merged = ensure_sales_schema(pd.concat(frames, ignore_index=True, sort=False))
    merged = _dedupe_orders(merged)

    if start_date:
        merged = merged[merged["order_date"] >= pd.to_datetime(start_date, errors="coerce")]
    if end_date:
        merged = merged[merged["order_date"] <= pd.to_datetime(end_date, errors="coerce") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)]

    merged = merged.sort_values("order_date", ascending=False, na_position="last")
    merged = merged.reset_index(drop=True)
    return merged


def get_data_summary() -> dict:
    df_hist = load_historical_data()
    df_live = load_live_2026_data()
    df_woo = load_woocommerce_live_data()
    df_stream = load_live_stream_data()
    return {
        "historical": len(df_hist),
        "live_2026": len(df_live),
        "woocommerce_live": len(df_woo),
        "live_stream": len(df_stream),
        "total": len(df_hist) + len(df_live) + len(df_woo) + len(df_stream),
    }
