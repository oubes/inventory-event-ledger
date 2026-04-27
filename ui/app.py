import sys
import os
from pathlib import Path

import streamlit as st
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analytics.aggregation import (
    aggregate_sales_by_time,
    sales_trend,
    product_contribution,
    detect_sales_periods,
    classify_sales_stability,
    aggregate_daily
)

st.set_page_config(page_title="Sales Analytics Engine", layout="wide")
st.title("Sales Analytics Engine")

BASE_OUTPUT = Path("outputs")

FREQ_MAP = {
    "D": "days",
    "M": "months"
}

def load_full_dataset():
    path = BASE_OUTPUT / "aggregated_selling"

    if not path.exists():
        return None

    frames = []

    for sub in ["days", "months"]:
        sub_path = path / sub

        if not sub_path.exists():
            continue

        for file in sub_path.glob("*.csv"):
            df = pd.read_csv(file)
            df["source_file"] = file.stem
            df["granularity"] = sub
            frames.append(df)

    if not frames:
        return None

    df = pd.concat(frames, ignore_index=True)

    if "start_datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["start_datetime"], errors="coerce")

    return df


def load_dataset(category: str, subfolder: str):
    path = BASE_OUTPUT / category / subfolder

    if not path.exists():
        return None

    files = list(path.glob("*.csv"))
    if not files:
        return None

    return {f.stem: pd.read_csv(f) for f in sorted(files)}


def load_single_file(category: str, filename: str):
    path = BASE_OUTPUT / category / filename

    if not path.exists():
        return None

    return pd.read_csv(path)


def flatten_dict(data: dict, group_col="__group__"):
    if not isinstance(data, dict):
        return data

    frames = []

    for k, v in data.items():
        if isinstance(v, pd.DataFrame):
            tmp = v.copy()
            tmp[group_col] = k
            frames.append(tmp)

    if not frames:
        return None

    return pd.concat(frames, ignore_index=True)


def paginated_dataframe(df: pd.DataFrame, key: str):
    if df is None or len(df) == 0:
        return

    total = len(df)

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        page_size = st.selectbox(
            "Page size",
            [20, 50, 100, 200],
            index=1,
            key=f"{key}_size"
        )

    pages = max((total - 1) // page_size + 1, 1)

    with col2:
        page = st.number_input(
            "Page",
            min_value=1,
            max_value=pages,
            value=1,
            key=f"{key}_page"
        )

    start = (page - 1) * page_size
    end = start + page_size

    with col3:
        st.caption(f"{start+1}-{min(end, total)} / {total}")

    st.dataframe(df.iloc[start:end], use_container_width=True)


df = load_full_dataset()

if df is None:
    st.stop()


st.sidebar.header("Controls")

analysis_type = st.sidebar.selectbox(
    "Select Analysis",
    [
        "Full Dataset",
        "Aggregate Daily",
        "Aggregate Sales By Time",
        "Sales Trend",
        "Product Contribution",
        "Sales Period Detection",
        "Sales Stability"
    ]
)


if analysis_type == "Full Dataset":
    st.write(f"{len(df)} rows")
    paginated_dataframe(df, "full")
    st.stop()


st.dataframe(df.head(), use_container_width=True)

st.divider()


if analysis_type == "Aggregate Daily":
    data = load_dataset("aggregated_time", "days")
    flat = flatten_dict(data)
    paginated_dataframe(flat, "daily")

elif analysis_type == "Aggregate Sales By Time":
    freq = st.selectbox("Frequency", ["D", "M"], key="agg")
    data = load_dataset("aggregated_selling", FREQ_MAP[freq])
    flat = flatten_dict(data)
    paginated_dataframe(flat, "agg")

elif analysis_type == "Sales Trend":
    freq = st.selectbox("Frequency", ["D", "M"], key="trend")
    data = load_dataset("trend", FREQ_MAP[freq])
    flat = flatten_dict(data)
    paginated_dataframe(flat, "trend")

elif analysis_type == "Product Contribution":
    data = load_single_file("contribution", "product_contribution.csv")

    if isinstance(data, pd.DataFrame):

        df_contrib = data.copy()

        for col in df_contrib.columns:
            if pd.api.types.is_numeric_dtype(df_contrib[col]):

                max_val = df_contrib[col].max()

                if max_val <= 1:
                    df_contrib[col] = (df_contrib[col] * 100).round(2).astype(str) + "%"

                elif max_val <= 100:
                    df_contrib[col] = df_contrib[col].round(2).astype(str) + "%"

        paginated_dataframe(df_contrib, "contrib")

elif analysis_type == "Sales Period Detection":
    freq = st.selectbox("Frequency", ["D", "M"], key="period")
    data = load_dataset("periods", FREQ_MAP[freq])
    flat = flatten_dict(data)
    paginated_dataframe(flat, "periods")

elif analysis_type == "Sales Stability":
    data = load_single_file("stability", "sales_stability.csv")
    paginated_dataframe(data, "stability")