import pandas as pd
import numpy as np

def aggregate_daily(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    grouped = df.groupby([
        "item_id",
        pd.Grouper(key="datetime", freq=freq),
        "operation"
    ])["quantity"].sum()

    return grouped.unstack(fill_value=0)

import pandas as pd

import pandas as pd

def aggregate_sales_by_time(df: pd.DataFrame, freq="M"):
    df = df.copy()

    df["datetime"] = pd.to_datetime(df["datetime"])
    if freq == "ME":
        freq = "M"

    sell_df = df[df["operation"] == "SELL"].copy()
    sell_df = sell_df.drop_duplicates()

    sell_df["time_bucket"] = sell_df["datetime"].dt.to_period(freq)

    result = (
        sell_df.groupby(["time_bucket", "item_id"])["quantity"]
        .sum()
        .reset_index()
    )

    result["rank"] = result.groupby("time_bucket")["quantity"] \
        .rank(ascending=False, method="dense") \
        .astype(int)

    result = result.sort_values(["time_bucket", "rank"])

    # split into separate tables per month
    tables = {
        str(bucket): group.drop(columns=["time_bucket"]).reset_index(drop=True)
        for bucket, group in result.groupby("time_bucket")
    }

    return tables


def sales_trend(df: pd.DataFrame, freq="M", threshold=0.0):
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])

    if freq == "ME":
        freq = "M"

    sell_df = df[df["operation"] == "SELL"].copy()
    if sell_df.empty:
        return {}

    sell_df["time_bucket"] = sell_df["datetime"].dt.to_period(freq)

    grouped = (
        sell_df.groupby(["time_bucket", "item_id"])["quantity"]
        .sum()
        .reset_index()
        .sort_values(["item_id", "time_bucket"])
    )

    result = {}

    for item_id, g in grouped.groupby("item_id"):
        g = g.sort_values("time_bucket").reset_index(drop=True)

        values = g["quantity"].astype(float)

        mom_change = [None]  # first month has no previous
        mom_label = ["N/A"]

        for i in range(1, len(values)):
            prev = values.iloc[i - 1]
            curr = values.iloc[i]

            if prev == 0:
                pct = 0
            else:
                pct = (curr - prev) / prev

            mom_change.append(float(pct))

            if pct > threshold:
                mom_label.append("increase")
            elif pct < -threshold:
                mom_label.append("decrease")
            else:
                mom_label.append("stable")

        g["mom_change"] = mom_change
        g["mom_label"] = mom_label

        result[item_id] = {
            "table": g
        }

    return result

def item_summary(df: pd.DataFrame, item_id: str):
    return aggregate_daily(df).loc[item_id]