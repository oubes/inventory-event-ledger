# ---- Imports ----
import pandas as pd

# -------------- Aggregation Functions --------------
# ---- Daily Aggregation ----
def aggregate_daily(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    grouped = df.groupby([
        "item_id",
        pd.Grouper(key="datetime", freq=freq),
        "operation"
    ])["quantity"].sum()

    return grouped.unstack(fill_value=0)

# ---- aggregate sales by time ----
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

 
# ---- Sales Trend Analysis ----
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

            mom_change.append(float(pct)) # type: ignore

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

# ---- Product Contribution ----
def product_contribution(df: pd.DataFrame, freq="overall"):
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])

    sell_df = df[df["operation"] == "SELL"].copy()
    if sell_df.empty:
        return {}

    if freq == "overall":
        total_sales = sell_df.groupby("item_id")["quantity"].sum()
        grand_total = total_sales.sum()

        result = total_sales.reset_index()
        result.columns = ["item_id", "total_sales"]

        result["contribution"] = (
            (result["total_sales"] / grand_total) * 100
        ).round(2)

        return result.sort_values("contribution", ascending=False)

    sell_df["time_bucket"] = sell_df["datetime"].dt.to_period(freq)

    grouped = (
        sell_df.groupby(["time_bucket", "item_id"])["quantity"]
        .sum()
        .reset_index()
    )

    grouped["period_total"] = grouped.groupby("time_bucket")["quantity"].transform("sum")

    grouped["contribution"] = (
        (grouped["quantity"] / grouped["period_total"]) * 100
    ).round(2)

    return grouped.sort_values(["time_bucket", "contribution"], ascending=[True, False])

# ---- Sales Period Detection ----
def detect_sales_periods(df: pd.DataFrame, freq="M", z_threshold=1.0):
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    
    if freq == "ME":
        freq = "M"

    # SELL only
    sell_df = df[df["operation"] == "SELL"].copy()
    if sell_df.empty:
        return pd.DataFrame()

    sell_df["time_bucket"] = sell_df["datetime"].dt.to_period(freq)

    # total sales per period
    period_sales = (
        sell_df.groupby("time_bucket")["quantity"]
        .sum()
        .reset_index()
        .sort_values("time_bucket")
    )

    values = period_sales["quantity"].astype(float)

    mean = values.mean()
    std = values.std() if values.std() != 0 else 1

    # z-score
    z_scores = (values - mean) / std

    labels = []

    for z in z_scores:
        if z >= z_threshold:
            labels.append("high_sales")
        elif z <= -z_threshold:
            labels.append("low_sales")
        else:
            labels.append("normal")

    period_sales["z_score"] = z_scores
    period_sales["regime"] = labels

    return period_sales

# ---- Sales Stability ----
def classify_sales_stability(df: pd.DataFrame, freq="M", threshold=0.3):
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    
    if freq == "ME":
        freq = "M"

    sell_df = df[df["operation"] == "SELL"].copy()
    if sell_df.empty:
        return pd.DataFrame()

    sell_df["time_bucket"] = sell_df["datetime"].dt.to_period(freq)

    grouped = (
        sell_df.groupby(["time_bucket", "item_id"])["quantity"]
        .sum()
        .reset_index()
    )

    result = []

    for item_id, g in grouped.groupby("item_id"):
        g = g.sort_values("time_bucket")

        values = g["quantity"].astype(float).values

        mean = values.mean() # type: ignore
        std = values.std() # type: ignore

        if mean == 0:
            cv = 0
        else:
            cv = std / mean

        if cv < threshold:
            label = "stable"
        else:
            label = "volatile"

        result.append({
            "item_id": item_id,
            "mean_sales": float(mean),
            "std_sales": float(std),
            "cv": float(cv),
            "stability": label
        })

    return pd.DataFrame(result).sort_values("cv", ascending=False)

# ---- Item Summary ----
def item_summary(df: pd.DataFrame, item_id: str):
    return aggregate_daily(df).loc[item_id]