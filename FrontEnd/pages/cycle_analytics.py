from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from BackEnd.utils.sales_schema import ensure_sales_schema
from .dashboard_lib.data_helpers import build_order_level_dataset


FRIDAY_WEEKDAY = 4
CYCLE_CUTOFF_HOUR = 17


def _cycle_anchor(dt: datetime) -> datetime:
    anchor = dt.replace(hour=CYCLE_CUTOFF_HOUR, minute=0, second=0, microsecond=0)
    if dt < anchor:
        anchor -= timedelta(days=1)
    return anchor


def _previous_business_boundary(boundary: datetime) -> datetime:
    cursor = boundary - timedelta(days=1)
    while cursor.weekday() == FRIDAY_WEEKDAY:
        cursor -= timedelta(days=1)
    return cursor


def get_business_cycles(now: datetime) -> tuple[datetime, datetime, datetime, datetime]:
    current_end = _cycle_anchor(now)
    current_start = _previous_business_boundary(current_end)
    previous_end = current_start
    previous_start = _previous_business_boundary(previous_end)
    return current_start, current_end, previous_start, previous_end


def prepare_cycle_orders(df: pd.DataFrame) -> pd.DataFrame:
    sales = ensure_sales_schema(df)
    if sales.empty:
        return pd.DataFrame()

    orders = build_order_level_dataset(sales).copy()
    orders["order_date"] = pd.to_datetime(orders.get("order_date"), errors="coerce")
    orders["shipped_date"] = pd.to_datetime(orders.get("shipped_date"), errors="coerce")
    status_series = orders.get("order_status", pd.Series("", index=orders.index)).astype(str).str.lower()
    orders["status_bucket"] = status_series.apply(
        lambda value: "shipped" if value in {"completed", "shipped"} else "new"
    )
    metric_dates = orders["order_date"].copy()
    shipped_mask = orders["status_bucket"] == "shipped"
    metric_dates.loc[shipped_mask] = orders.loc[shipped_mask, "shipped_date"].fillna(
        orders.loc[shipped_mask, "order_date"]
    )
    orders["metric_date"] = pd.to_datetime(metric_dates, errors="coerce")
    return orders


def calculate_cycle_metrics(
    orders_df: pd.DataFrame,
    cycle_start: datetime,
    cycle_end: datetime,
    status_bucket: str,
) -> dict[str, float]:
    if orders_df.empty:
        return {"num_orders": 0, "items_sold": 0, "revenue": 0.0}

    scoped = orders_df[orders_df["status_bucket"] == status_bucket].copy()
    scoped = scoped[scoped["metric_date"].between(cycle_start, cycle_end, inclusive="right")]
    return {
        "num_orders": int(scoped["order_id"].nunique()) if "order_id" in scoped.columns else int(len(scoped)),
        "items_sold": int(pd.to_numeric(scoped.get("qty", 0), errors="coerce").fillna(0).sum()),
        "revenue": float(pd.to_numeric(scoped.get("order_total", 0), errors="coerce").fillna(0).sum()),
    }
