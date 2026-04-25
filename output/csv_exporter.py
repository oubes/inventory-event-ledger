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


def export_item_tables(df: pd.DataFrame, output_dir: str, freq: str = "D") -> None:
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    aggregated_by_time = aggregate_daily(df, freq)

    aggregated_by_selling = aggregate_sales_by_time(df, freq)

    sales_by_trend = sales_trend(df, freq)

    product_contribution_result = product_contribution(df)
    
    
    detect_sales_periods_result = detect_sales_periods(df, freq)
    
    classify_sales_stability_result = classify_sales_stability(df)
    print(classify_sales_stability_result)
        
    exported_files = 0

    for item_id in aggregated_by_time.index.get_level_values(0).unique():
        item_df = aggregated_by_time.loc[item_id].reset_index()

        file_path = output_path / f"{item_id}_{freq}.csv"

        item_df.to_csv(file_path, index=False)

        print(
            f"[SAVED] item_id={item_id} | "
            f"rows={len(item_df)} | "
            f"path={file_path}"
        )

        exported_files += 1

    print(f"\n[DONE] Exported {exported_files} aggregated files → {output_path}")