"""Traditional EDA helpers for tabular banking datasets.

These utilities are intentionally pandas-only so they can run in lightweight
notebook environments without requiring additional visualization libraries.
"""

from __future__ import annotations

from typing import Any, Dict

from .dataset_loader import _require_pandas


def run_traditional_eda(frame, top_n: int = 10) -> Dict[str, Any]:
    """Compute a compact but comprehensive EDA summary for a DataFrame.

    Args:
        frame: Input pandas DataFrame.
        top_n: Number of top values to keep for categorical distributions.

    Returns:
        Dictionary of EDA artifacts (mostly pandas DataFrames) covering key
        structural, missingness, numerical, and categorical diagnostics.
    """

    pd = _require_pandas()

    if frame is None:
        raise ValueError("'frame' cannot be None.")

    total_rows = int(len(frame))
    total_columns = int(len(frame.columns))
    duplicate_rows = int(frame.duplicated().sum())

    overview = {
        "row_count": total_rows,
        "column_count": total_columns,
        "duplicate_row_count": duplicate_rows,
        "duplicate_row_pct": round((duplicate_rows / total_rows * 100), 2) if total_rows else 0.0,
        "memory_usage_mb": round(float(frame.memory_usage(deep=True).sum()) / (1024**2), 4),
    }

    dtypes = (
        frame.dtypes.astype(str)
        .rename("dtype")
        .to_frame()
        .assign(non_null=lambda x: frame.notna().sum().astype(int).values)
        .assign(null_count=lambda x: frame.isna().sum().astype(int).values)
        .assign(null_pct=lambda x: ((x["null_count"] / total_rows * 100) if total_rows else 0).round(2))
        .sort_values(by=["null_pct", "dtype"], ascending=[False, True])
    )

    numeric_cols = frame.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = frame.select_dtypes(exclude=["number", "datetime"]).columns.tolist()

    if numeric_cols:
        numerical_summary = frame[numeric_cols].describe().T
        additional_stats = frame[numeric_cols].agg(["skew", "kurt"]).T.rename(columns={"kurt": "kurtosis"})
        numerical_summary = numerical_summary.join(additional_stats, how="left").sort_values("std", ascending=False)

        q1 = frame[numeric_cols].quantile(0.25)
        q3 = frame[numeric_cols].quantile(0.75)
        iqr = q3 - q1
        outlier_mask = (frame[numeric_cols] < (q1 - 1.5 * iqr)) | (frame[numeric_cols] > (q3 + 1.5 * iqr))
        outlier_summary = pd.DataFrame(
            {
                "outlier_count": outlier_mask.sum().astype(int),
                "outlier_pct": ((outlier_mask.sum() / total_rows * 100) if total_rows else 0).round(2),
            }
        ).sort_values("outlier_pct", ascending=False)

        correlation_matrix = frame[numeric_cols].corr(numeric_only=True)
    else:
        numerical_summary = pd.DataFrame()
        outlier_summary = pd.DataFrame()
        correlation_matrix = pd.DataFrame()

    if categorical_cols:
        cardinality = (
            frame[categorical_cols]
            .nunique(dropna=False)
            .rename("unique_count")
            .to_frame()
            .assign(unique_pct=lambda x: ((x["unique_count"] / total_rows * 100) if total_rows else 0).round(2))
            .sort_values("unique_count", ascending=False)
        )

        top_values: Dict[str, Any] = {}
        for column in categorical_cols:
            value_dist = (
                frame[column]
                .astype("string")
                .fillna("<NULL>")
                .value_counts(dropna=False)
                .head(top_n)
                .rename_axis("value")
                .reset_index(name="count")
            )
            value_dist["pct"] = ((value_dist["count"] / total_rows * 100) if total_rows else 0).round(2)
            top_values[column] = value_dist
    else:
        cardinality = pd.DataFrame()
        top_values = {}

    return {
        "overview": overview,
        "schema_and_missingness": dtypes,
        "numerical_summary": numerical_summary,
        "numerical_outlier_summary": outlier_summary,
        "correlation_matrix": correlation_matrix,
        "categorical_cardinality": cardinality,
        "categorical_top_values": top_values,
    }
