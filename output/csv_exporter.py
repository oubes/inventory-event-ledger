import pandas as pd
from pathlib import Path


def export_item_tables(df: pd.DataFrame, output_dir: str) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for item_id, item_df in df.groupby("item_id"):
        file_path = output_path / f"{item_id}.csv"

        item_df_sorted = item_df.sort_values("datetime")

        item_df_sorted.to_csv(file_path, index=False)

    print(f"Exported {df['item_id'].nunique()} files to {output_dir}")