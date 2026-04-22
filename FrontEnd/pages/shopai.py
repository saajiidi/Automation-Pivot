from __future__ import annotations

import re
from typing import Iterable

import pandas as pd


def _normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if digits.startswith("88") and len(digits) > 11:
        digits = digits[-11:]
    if len(digits) == 10 and digits.startswith("1"):
        digits = "0" + digits
    return digits[-11:] if len(digits) >= 11 else digits


def _customer_lookup(customers_df: pd.DataFrame) -> pd.DataFrame:
    if customers_df is None or customers_df.empty:
        return pd.DataFrame()

    lookup = customers_df.copy()
    lookup["primary_name_norm"] = lookup.get("primary_name", "").astype(str).str.strip().str.lower()
    lookup["phone_tokens"] = lookup.get("all_phones", "").astype(str).str.split(",")
    lookup["phone_tokens"] = lookup["phone_tokens"].apply(
        lambda values: {_normalize_phone(value) for value in values if str(value).strip()}
    )
    return lookup


def build_shopai_conversation_frame(conversations: Iterable[dict], customers_df: pd.DataFrame) -> pd.DataFrame:
    frame = pd.DataFrame(list(conversations or []))
    if frame.empty:
        return frame

    lookup = _customer_lookup(customers_df)
    if lookup.empty:
        return frame

    enriched_rows = []
    for _, row in frame.iterrows():
        phone = _normalize_phone(row.get("customer_id", ""))
        name_norm = str(row.get("customer", "")).strip().lower()

        match = lookup[lookup["phone_tokens"].apply(lambda phones: phone and phone in phones)]
        if match.empty and name_norm:
            match = lookup[lookup["primary_name_norm"] == name_norm]

        enriched = row.to_dict()
        if not match.empty:
            customer = match.iloc[0]
            for field in ["segment", "total_orders", "total_revenue", "favorite_product", "recency_days", "primary_name"]:
                if field in customer.index:
                    enriched[field] = customer[field]
            enriched["linked_customer"] = True
        else:
            enriched["linked_customer"] = False
        enriched_rows.append(enriched)

    return pd.DataFrame(enriched_rows)


def build_shopai_crm_summary(conversations: Iterable[dict], customers_df: pd.DataFrame) -> dict:
    frame = build_shopai_conversation_frame(conversations, customers_df)
    if frame.empty:
        return {
            "kpis": {"conversations": 0, "needs_attention": 0, "linked_customers": 0, "resolution_rate": 0.0},
            "recommendations": [],
            "frame": frame,
        }

    statuses = frame.get("status", pd.Series("", index=frame.index)).astype(str).str.lower()
    needs_attention = statuses.isin(["escalated", "open", "pending"]).sum()
    resolved = statuses.eq("resolved").sum()
    linked_customers = int(frame.get("linked_customer", pd.Series(False, index=frame.index)).fillna(False).sum())
    resolution_rate = (resolved / len(frame) * 100) if len(frame) else 0.0

    recommendations: list[str] = []
    vip_attention = frame[
        frame.get("segment", pd.Series("", index=frame.index)).astype(str).str.contains("VIP", case=False, na=False)
        & statuses.isin(["escalated", "open", "pending"])
    ]
    if not vip_attention.empty:
        recommendations.append("Prioritize VIP conversations in the escalation queue to protect retention.")
    if needs_attention and frame.get("response_minutes") is not None:
        avg_response = pd.to_numeric(frame["response_minutes"], errors="coerce").fillna(0).mean()
        if avg_response > 3:
            recommendations.append("Response time is slipping on active threads; tighten first-response handling.")
    if linked_customers < len(frame):
        recommendations.append("Improve identity linking for social handles and phone normalization to enrich CRM context.")

    return {
        "kpis": {
            "conversations": int(len(frame)),
            "needs_attention": int(needs_attention),
            "linked_customers": linked_customers,
            "resolution_rate": round(resolution_rate, 1),
        },
        "recommendations": recommendations,
        "frame": frame,
    }
