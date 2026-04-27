import sys
import os
from pathlib import Path

import streamlit as st
import pandas as pd

# ---------------- Path Fix ----------------
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analytics.aggregation import (
    aggregate_sales_by_time,
    sales_trend,
    product_contribution,
    detect_sales_periods,
    classify_sales_stability,
    item_summary,
    aggregate_daily
)

# ---------------- Config ----------------
st.set_page_config(page_title="Sales Analytics Engine", layout="wide")
st.title("📊 Sales Analytics Engine")

BASE_OUTPUT = Path("outputs")

# ---------------- GRANULARITY MAP ----------------
FREQ_MAP = {
    "D": "days",
    "M": "months"
}

# ---------------- LOAD FULL DATA ----------------
def load_full_dataset():
    path = BASE_OUTPUT / "aggregated_selling"

    if not path.exists():
        return None

    all_data = []

    for sub in ["days", "months"]:
        sub_path = path / sub

        if not sub_path.exists():
            continue

        for file in sub_path.glob("*.csv"):
            df_part = pd.read_csv(file)

            df_part["source_file"] = file.stem
            df_part["granularity"] = sub

            all_data.append(df_part)

    if not all_data:
        return None

    df = pd.concat(all_data, ignore_index=True)

    if "start_datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["start_datetime"], errors="coerce")

    return df


# ---------------- LOADERS ----------------
def load_dataset(category: str, subfolder: str):
    path = BASE_OUTPUT / category / subfolder

    if not path.exists():
        return None

    files = list(path.glob("*.csv"))
    if not files:
        return None

    return {
        f.stem: pd.read_csv(f)
        for f in sorted(files)
    }


def load_single_file(category: str, filename: str):
    path = BASE_OUTPUT / category / filename

    if not path.exists():
        return None

    return pd.read_csv(path)


# ---------------- FLATTEN DICT ----------------
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


# ---------------- PAGINATION ----------------
def paginated_dataframe(df: pd.DataFrame, key: str):
    if df is None or len(df) == 0:
        st.write("No data available")
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


# ---------------- ULTRA CLEAN DATAFRAME SANITIZER ----------------
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        return df

    df = df.copy()

    # 🔴 remove known noisy / leakage columns
    noisy_cols = [
        "operation",
        "Unnamed: 0",
        "index",
        "level_0"
    ]

    for col in noisy_cols:
        if col in df.columns:
            df = df.drop(columns=[col])

    # 🔴 fix column metadata artifacts
    df.columns.name = None

    # 🔴 reset index safely
    df = df.reset_index(drop=True)

    # 🔴 remove invalid numeric values
    df = df.replace([float("inf"), float("-inf")], None)

    return df


# ---------------- RENDER ----------------
def render(obj, key="table"):
    if isinstance(obj, pd.DataFrame):
        paginated_dataframe(obj, key=key)
        return

    if isinstance(obj, dict):
        flat = flatten_dict(obj)

        if flat is None:
            st.warning("No valid data found")
            return

        if "__group__" in flat.columns:
            groups = sorted(flat["__group__"].dropna().unique().tolist())

            selected = st.selectbox(
                "Select Group",
                ["ALL"] + groups,
                key=f"{key}_group"
            )

            if selected != "ALL":
                flat = flat[flat["__group__"] == selected]

        paginated_dataframe(flat, key=f"{key}_flat")
        return

    st.write(obj)


# ---------------- DATA ----------------
df = load_full_dataset()

if df is None:
    st.error("No data found in outputs/. Run pipeline first.")
    st.stop()


# ---------------- SIDEBAR ----------------
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
        "Sales Stability",
        "Item Summary"
    ]
)


# ---------------- FULL DATA ----------------
if analysis_type == "Full Dataset":
    st.subheader("📦 Full Dataset (All Outputs Combined)")
    st.write(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
    paginated_dataframe(df, key="full")
    st.stop()


# ---------------- PREVIEW ----------------
st.subheader("📊 Data Preview")
st.dataframe(df.head(), use_container_width=True)

st.divider()


# ---------------- ANALYTICS ----------------

if analysis_type == "Aggregate Daily":
    st.subheader("📅 Daily Aggregation")
    render(load_dataset("aggregated_time", "days"), key="daily")

elif analysis_type == "Aggregate Sales By Time":
    st.subheader("📦 Sales By Time")

    freq_local = st.selectbox("Frequency", ["D", "M"], key="agg_time_freq")
    render(load_dataset("aggregated_selling", FREQ_MAP[freq_local]), key="agg_time")

elif analysis_type == "Sales Trend":
    st.subheader("📈 Sales Trend")

    freq_local = st.selectbox("Frequency", ["D", "M"], key="trend_freq")
    render(load_dataset("trend", FREQ_MAP[freq_local]), key="trend")

elif analysis_type == "Product Contribution":
    st.subheader("📊 Product Contribution")
    render(load_single_file("contribution", "product_contribution.csv"), key="contrib")

elif analysis_type == "Sales Period Detection":
    st.subheader("⚡ Sales Regimes")

    freq_local = st.selectbox("Frequency", ["D", "M"], key="period_freq")
    render(load_dataset("periods", FREQ_MAP[freq_local]), key="periods")

elif analysis_type == "Sales Stability":
    st.subheader("📉 Sales Stability")
    render(load_single_file("stability", "sales_stability.csv"), key="stability")

# ---------------- ITEM SUMMARY (FULL FIXED PIPELINE) ----------------
elif analysis_type == "Item Summary":
    st.subheader("📌 Item Summary")

    item_ids = (
        sorted(df["item_id"].dropna().unique().tolist())
        if "item_id" in df.columns
        else []
    )

    if not item_ids:
        st.warning("No items available in dataset")
    else:
        item_id = st.selectbox(
            "Select Item ID",
            options=item_ids,
            index=None,
            placeholder="Choose an item..."
        )

        if item_id is not None:
            try:
                result = item_summary(df, item_id)

                result = clean_dataframe(result)

                if isinstance(result, pd.DataFrame):
                    result = result.loc[:, ~result.columns.duplicated()]

                paginated_dataframe(result, key="item_summary")

            except Exception as e:
                st.error(str(e))