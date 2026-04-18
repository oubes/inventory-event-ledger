import pandas as pd

def aggregate_daily(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby([
        "item_id",
        pd.Grouper(key="datetime", freq="D"),
        "operation"
    ])["quantity"].sum()

    return grouped.unstack(fill_value=0)


def item_summary(df: pd.DataFrame, item_id: str):
    return aggregate_daily(df).loc[item_id]