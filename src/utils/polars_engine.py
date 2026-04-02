"""
Polars-based Data Processing Optimization

Provides high-performance data processing functions using Polars instead of Pandas
for large datasets (10-100x faster).
"""

from typing import Optional
import pandas as pd
import numpy as np

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


def to_polars(df: pd.DataFrame) -> Optional["pl.DataFrame"]:
    """Convert pandas DataFrame to polars DataFrame."""
    if not POLARS_AVAILABLE or df is None:
        return None
    return pl.from_pandas(df)


def to_pandas(df: "pl.DataFrame") -> pd.DataFrame:
    """Convert polars DataFrame to pandas DataFrame."""
    if df is None:
        return pd.DataFrame()
    return df.to_pandas()


def fast_groupby_sum(
    df: pd.DataFrame,
    group_col: str,
    sum_cols: list[str]
) -> pd.DataFrame:
    """
    High-performance groupby sum using Polars if available.
    Falls back to Pandas if Polars is not installed.
    """
    if not POLARS_AVAILABLE or len(df) < 1000:
        # Use pandas for small datasets or when polars unavailable
        return df.groupby(group_col)[sum_cols].sum().reset_index()
    
    # Use polars for large datasets
    pl_df = to_polars(df)
    if pl_df is None:
        return df.groupby(group_col)[sum_cols].sum().reset_index()
    
    agg_exprs = [pl.sum(col).alias(col) for col in sum_cols]
    result = pl_df.group_by(group_col).agg(agg_exprs)
    return to_pandas(result)


def fast_read_csv(path: str) -> pd.DataFrame:
    """
    Fast CSV reading using Polars lazy evaluation.
    Falls back to pandas if polars unavailable.
    """
    if POLARS_AVAILABLE:
        try:
            pl_df = pl.read_csv(path, infer_schema_length=10000)
            return to_pandas(pl_df)
        except Exception:
            pass
    
    return pd.read_csv(path)


def fast_read_parquet(path: str) -> pd.DataFrame:
    """
    Fast Parquet reading using Polars.
    Falls back to pandas if polars unavailable.
    """
    if POLARS_AVAILABLE:
        try:
            pl_df = pl.read_parquet(path)
            return to_pandas(pl_df)
        except Exception:
            pass
    
    return pd.read_parquet(path)


def fast_join(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: str,
    how: str = "inner"
) -> pd.DataFrame:
    """High-performance DataFrame join using Polars if available."""
    if not POLARS_AVAILABLE or len(left) < 1000:
        return left.merge(right, on=on, how=how)
    
    pl_left = to_polars(left)
    pl_right = to_polars(right)
    
    if pl_left is None or pl_right is None:
        return left.merge(right, on=on, how=how)
    
    result = pl_left.join(pl_right, on=on, how=how)
    return to_pandas(result)


def fast_pivot(
    df: pd.DataFrame,
    index: str,
    columns: str,
    values: str
) -> pd.DataFrame:
    """High-performance pivot operation."""
    if not POLARS_AVAILABLE or len(df) < 1000:
        return df.pivot(index=index, columns=columns, values=values)
    
    pl_df = to_polars(df)
    if pl_df is None:
        return df.pivot(index=index, columns=columns, values=values)
    
    # Polars pivot
    result = pl_df.pivot(index=index, columns=columns, values=values)
    return to_pandas(result)


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize DataFrame memory usage by downcasting types."""
    df_optimized = df.copy()
    
    # Downcast integers
    int_cols = df_optimized.select_dtypes(include=[np.integer]).columns
    for col in int_cols:
        df_optimized[col] = pd.to_numeric(df_optimized[col], downcast="integer")
    
    # Downcast floats
    float_cols = df_optimized.select_dtypes(include=[np.floating]).columns
    for col in float_cols:
        df_optimized[col] = pd.to_numeric(df_optimized[col], downcast="float")
    
    # Convert object columns to category if beneficial
    obj_cols = df_optimized.select_dtypes(include=["object"]).columns
    for col in obj_cols:
        num_unique = df_optimized[col].nunique()
        num_total = len(df_optimized[col])
        if num_unique / num_total < 0.5:  # Less than 50% unique values
            df_optimized[col] = df_optimized[col].astype("category")
    
    return df_optimized


# Lazy evaluation for large datasets
def lazy_query(df: pd.DataFrame) -> Optional["pl.LazyFrame"]:
    """Create a lazy Polars query for deferred execution."""
    if not POLARS_AVAILABLE:
        return None
    
    pl_df = to_polars(df)
    if pl_df is None:
        return None
    
    return pl_df.lazy()
