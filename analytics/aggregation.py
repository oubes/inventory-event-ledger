import pandas as pd

def aggregate_daily(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    grouped = df.groupby([
        "item_id",
        pd.Grouper(key="datetime", freq=freq),
        "operation"
    ])["quantity"].sum()

    return grouped.unstack(fill_value=0)


def item_summary(df: pd.DataFrame, item_id: str):
    return aggregate_daily(df).loc[item_id]