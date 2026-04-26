import pandas as pd
from pathlib import Path

from analytics.aggregation import (
    aggregate_daily,
    aggregate_sales_by_time,
    sales_trend,
    product_contribution,
    detect_sales_periods,
    classify_sales_stability
)


def _prepare_path(output_dir: str):
    path = Path(output_dir).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_grouped_csv(data: pd.DataFrame | dict[str, pd.DataFrame], output_path: Path, freq: str | None = None):
    if isinstance(data, dict):
        for item_id, item_df in data.items():
            file_name = f"{item_id}.csv" if freq is None else f"{item_id}_{freq}.csv"
            item_df.to_csv(output_path / file_name, index=False)
        return

    for item_id in data.index.get_level_values(0).unique():
        item_df = data.loc[item_id].reset_index()
        file_name = f"{item_id}.csv" if freq is None else f"{item_id}_{freq}.csv"
        item_df.to_csv(output_path / file_name, index=False)


def export_aggregated_by_time(df: pd.DataFrame, output_dir: str, freq: str):
    output_path = _prepare_path(output_dir)
    data = aggregate_daily(df, freq)
    _write_grouped_csv(data, output_path, freq)


def export_aggregated_by_selling(df: pd.DataFrame, output_dir: str, freq: str):
    output_path = _prepare_path(output_dir)
    data = aggregate_sales_by_time(df, freq)
    _write_grouped_csv(data, output_path, freq)


def export_sales_trend(df: pd.DataFrame, output_dir: str, freq: str):
    output_path = _prepare_path(output_dir)
    data = sales_trend(df, freq)

    cleaned = {}

    for item_id, value in data.items():
        # unwrap {"table": df}
        if isinstance(value, dict) and "table" in value:
            cleaned[item_id] = value["table"]
        else:
            cleaned[item_id] = value

    _write_grouped_csv(cleaned, output_path, freq)


def export_detect_sales_periods(df: pd.DataFrame, output_dir: str, freq: str):
    output_path = _prepare_path(output_dir)
    data = detect_sales_periods(df, freq)
    _write_grouped_csv(data, output_path, freq)


def export_product_contribution(df: pd.DataFrame, output_dir: str):
    output_path = _prepare_path(output_dir)
    data = product_contribution(df)

    if isinstance(data, dict):
        for item_id, item_df in data.items():
            item_df.to_csv(output_path / f"{item_id}.csv", index=False)
    else:
        data.to_csv(output_path / "product_contribution.csv", index=False)


def export_sales_stability(df: pd.DataFrame, output_dir: str):
    output_path = _prepare_path(output_dir)
    data = classify_sales_stability(df)

    data.to_csv(output_path / "sales_stability.csv", index=False)