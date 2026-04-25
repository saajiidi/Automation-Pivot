"""Category and Sub-category Sales Matrix View.

Renders a responsive CSS-grid dashboard card for each main category,
showing sub-categories/products, order counts, and revenue trends.
"""

import pandas as pd
import streamlit as st
from datetime import timedelta
from typing import Optional

from BackEnd.utils.woocommerce_helpers import format_currency
from BackEnd.core.logging_config import get_logger

logger = get_logger("category_matrix")

def render_category_matrix(
    sales_df: pd.DataFrame, 
    cat_col: str = "Category",
    subcat_col: str = "_clean_name", 
    val_col: str = "total",
    order_col: str = "order_id",
    date_col: str = "date_created"
) -> None:
    """Render the HTML matrix view for category and sub-category sales data."""
    if sales_df is None or sales_df.empty:
        st.info("No sales data available for matrix view.")
        return

    df = sales_df.copy()
    
    # 1. Column normalization & Fallbacks
    if cat_col not in df.columns:
        df[cat_col] = "Uncategorized"
    if subcat_col not in df.columns:
        df[subcat_col] = df.get("item_name", "Unknown Product")
    if val_col not in df.columns:
        val_col = "order_total" if "order_total" in df.columns else "line_total"
        if val_col not in df.columns:
            df[val_col] = 0.0
            
    if order_col not in df.columns:
        df[order_col] = df.index  # fallback for counting

    # 2. Date grouping for Week-over-Week (WoW) Comparison
    df['period'] = 'current'
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        valid_dates = df[df[date_col].notna()][date_col]
        if not valid_dates.empty:
            max_date = valid_dates.max()
            current_period_start = max_date - timedelta(days=7)
            prev_period_start = current_period_start - timedelta(days=7)
            
            df['period'] = 'older'
            df.loc[df[date_col] >= current_period_start, 'period'] = 'current'
            df.loc[(df[date_col] >= prev_period_start) & (df[date_col] < current_period_start), 'period'] = 'previous'

    # 3. CSS Injection (Scoping generic classes slightly to avoid Streamlit conflicts)
    css = """
    <style>
        .matrix-dashboard-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
            align-items: start;
            width: 100%;
            margin: 0 auto;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
        }
        .matrix-card {
            background: white;
            border-radius: 1rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: all 0.2s;
            border: 1px solid #e2e8f0;
        }
        .matrix-card-header {
            padding: 1rem 1.25rem;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.5rem;
            border-radius: 1rem 1rem 0 0;
        }
        .matrix-title-section {
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }
        .matrix-title-section h3 {
            font-size: 1.1rem;
            font-weight: 600;
            color: #0f172a;
            margin: 0;
        }
        .matrix-icon {
            font-size: 1.4rem;
            background: #eef2ff;
            padding: 0.3rem;
            border-radius: 12px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2.2rem;
            height: 2.2rem;
        }
        .matrix-comparison-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 2rem;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .matrix-positive { color: #10b981; background: #d1fae5; }
        .matrix-negative { color: #ef4444; background: #fee2e2; }
        .matrix-neutral { color: #64748b; background: #f1f5f9; }
        .matrix-scroll {
            overflow-x: auto;
            overflow-y: hidden;
            width: 100%;
            scroll-behavior: smooth;
        }
        .matrix-table {
            min-width: 500px;
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }
        .matrix-table th, .matrix-table td {
            padding: 0.9rem 1rem;
            text-align: left;
            border-bottom: 1px solid #eef2f6;
            white-space: nowrap;
            color: #334155;
        }
        .matrix-table th {
            background-color: #fafcff;
            font-weight: 600;
            color: #1e293b;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }
        .matrix-revenue { font-weight: 700; color: #0f172a; }
        .matrix-trend {
            display: inline-flex;
            align-items: center;
            gap: 0.2rem;
            font-weight: 500;
            font-size: 0.8rem;
            background: #f8fafc;
            padding: 0.2rem 0.5rem;
            border-radius: 1rem;
        }
        .matrix-trend-up { color: #10b981; }
        .matrix-trend-down { color: #ef4444; }
        .matrix-view-icon { cursor: pointer; font-size: 1.2rem; opacity: 0.7; transition: 0.1s; }
        .matrix-view-icon:hover { opacity: 1; }
        .matrix-card-footer {
            padding: 0.75rem 1.25rem;
            font-size: 0.75rem;
            color: #64748b;
            text-align: right;
            background: #fafcff;
            border-radius: 0 0 1rem 1rem;
        }
        @media (max-width: 1280px) {
            .matrix-dashboard-grid { grid-template-columns: 1fr; gap: 1.2rem; }
        }
        .matrix-scroll::-webkit-scrollbar { height: 6px; }
        .matrix-scroll::-webkit-scrollbar-track { background: #e2e8f0; border-radius: 4px; }
        .matrix-scroll::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 4px; }
    </style>
    """

    def get_cat_icon(cat_name):
        cat_lower = str(cat_name).lower()
        if any(w in cat_lower for w in ['electronic', 'tech', 'phone']): return '📱'
        if any(w in cat_lower for w in ['fashion', 'cloth', 'apparel', 'wear']): return '👗'
        if any(w in cat_lower for w in ['home', 'furn', 'living']): return '🛒'
        if any(w in cat_lower for w in ['beauty', 'health', 'cosmetic']): return '💄'
        return '📦'

    cards_html = ""
    
    # 4. Generate Cards by Category (Sorted by Top Revenue)
    cat_metrics = df.groupby(cat_col)[val_col].sum().sort_values(ascending=False)
    
    for cat in cat_metrics.index:
        cat_df = df[df[cat_col] == cat]
        
        curr_df = cat_df[cat_df['period'] == 'current']
        prev_df = cat_df[cat_df['period'] == 'previous']
        
        curr_cat_rev = curr_df[val_col].sum()
        prev_cat_rev = prev_df[val_col].sum()
        
        cat_growth = ((curr_cat_rev - prev_cat_rev) / prev_cat_rev * 100) if prev_cat_rev > 0 else 0
        badge_class = "matrix-positive" if cat_growth >= 0 else "matrix-negative"
        badge_text = f"+{cat_growth:.1f}% vs prev week" if cat_growth >= 0 else f"{cat_growth:.1f}% vs prev week"
        
        if prev_cat_rev == 0 and curr_cat_rev > 0:
            badge_text, badge_class = "New Sales", "matrix-positive"
        elif prev_cat_rev == 0 and curr_cat_rev == 0:
            badge_text, badge_class = "No change", "matrix-neutral"

        # 5. Generate Rows by Sub-Category (Top 10)
        sub_metrics = cat_df.groupby(subcat_col).agg({
            val_col: 'sum', order_col: 'nunique'
        }).rename(columns={val_col: 'rev_total', order_col: 'orders_total'}).sort_values('rev_total', ascending=False).head(10)
        
        rows_html = ""
        for subcat, row in sub_metrics.iterrows():
            sub_curr = curr_df[curr_df[subcat_col] == subcat][val_col].sum()
            sub_prev = prev_df[prev_df[subcat_col] == subcat][val_col].sum()
            
            sub_growth = ((sub_curr - sub_prev) / sub_prev * 100) if sub_prev > 0 else 0
            if sub_prev == 0 and sub_curr > 0:
                trend_html = '<span class="matrix-trend matrix-trend-up">▲ New</span>'
            elif sub_growth > 0:
                trend_html = f'<span class="matrix-trend matrix-trend-up">▲ +{sub_growth:.1f}%</span>'
            elif sub_growth < 0:
                trend_html = f'<span class="matrix-trend matrix-trend-down">▼ {sub_growth:.1f}%</span>'
            else:
                trend_html = '<span class="matrix-trend">➖ 0%</span>'
            
            rows_html += f"""
            <tr>
                <td>{subcat}</td>
                <td>{int(row['orders_total']):,}</td>
                <td class="matrix-revenue">{format_currency(row['rev_total'])}</td>
                <td>{trend_html}</td>
                <td class="matrix-view-icon">👁️</td>
            </tr>
            """

        cards_html += f"""
        <div class="matrix-card">
            <div class="matrix-card-header">
                <div class="matrix-title-section">
                    <span class="matrix-icon">{get_cat_icon(cat)}</span>
                    <h3>{cat} · Revenue Matrix</h3>
                </div>
                <div class="matrix-comparison-badge {badge_class}">{badge_text}</div>
            </div>
            <div class="matrix-scroll">
                <table class="matrix-table">
                    <thead>
                        <tr><th>Sub-Category</th><th>Total Orders</th><th>Revenue</th><th>vs Prev week</th><th>View</th></tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
            <div class="matrix-card-footer">WoW comparison · Top Sub-Categories</div>
        </div>
        """

    st.markdown(f"{css}<div class='matrix-dashboard-grid'>{cards_html}</div>", unsafe_allow_html=True)