from __future__ import annotations

import pandas as pd


_PREVIEW_COLUMN_GROUPS = [
    ["Order Number", "Order ID"],
    ["Order Date"],
    ["Shipped Date"],
    ["Customer Name", "Full Name (Billing)"],
    ["Tracking"],
    ["Item Name", "Product Name (main)"],
    ["Qty", "Quantity"],
    ["Order Total Amount"],
]


def _resolve_preview_columns(df: pd.DataFrame) -> list[str]:
    columns = list(df.columns)
    resolved: list[str] = []
    for candidates in _PREVIEW_COLUMN_GROUPS:
        match = next((candidate for candidate in candidates if candidate in columns), None)
        if match:
            resolved.append(match)
    return resolved
