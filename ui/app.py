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

# ---------------- Output Base Path ----------------
BASE_OUTPUT = Path("outputs")

# ---------------- Data Loader ----------------
def load_dataset(category: str, subfolder: str):
    """
    Loads CSVs from precomputed pipeline outputs
    """
    path = BASE_OUTPUT / category / subfolder

    if not path.exists():
        return None

    files = list(path.glob("*.csv"))
    if not files:
        return None

    # load all files in folder (not just latest)
    data = {
        f.stem: pd.read_csv(f)
        for f in sorted(files)
    }

    return data


def load_single_file(category: str, filename: str):
    """
    Load single aggregated file (like contribution/stability)
    """
    path = BASE_OUTPUT / category / filename

    if not path.exists():
        return None

    return pd.read_csv(path)

# ---------------- Renderer ----------------
def render_output(obj):
    if isinstance(obj, pd.DataFrame):
        st.dataframe(obj)

    elif isinstance(obj, dict):
        for k, v in obj.items():
            st.markdown(f"### {k}")

            if isinstance(v, pd.DataFrame):
                st.dataframe(v)
            else:
                st.write(v)

    else:
        st.write(obj)

# ---------------- Sidebar ----------------
st.sidebar.header("Controls")

analysis_type = st.sidebar.selectbox(
    "Select Analysis",
    [
        "Aggregate Daily",
        "Aggregate Sales By Time",
        "Sales Trend",
        "Product Contribution",
        "Sales Period Detection",
        "Sales Stability",
        "Item Summary"
    ]
)

freq = st.sidebar.selectbox("Frequency", ["D", "W", "M"])
threshold = st.sidebar.slider("Threshold", 0.0, 2.0, 1.0, 0.1)
item_id_input = st.sidebar.text_input("Item ID (for Item Summary)")

# ---------------- Data Mode ----------------
st.sidebar.divider()
st.sidebar.subheader("Data Source")

data_mode = st.sidebar.radio(
    "Mode",
    ["Precomputed Outputs"]
)

# ---------------- Load Base Data ----------------
# (we assume outputs exist → derived from pipeline)

df = None

# try to load any available dataset
sample_paths = [
    BASE_OUTPUT / "aggregated_selling" / "days",
    BASE_OUTPUT / "aggregated_selling" / "months"
]

for p in sample_paths:
    if p.exists():
        files = list(p.glob("*.csv"))
        if files:
            df = pd.read_csv(files[0])
            break

if df is None:
    st.error("No data found in outputs/. Run pipeline first.")
    st.stop()

df["datetime"] = pd.to_datetime(df["datetime"])

st.subheader("Sample Data Preview")
st.dataframe(df.head())

st.divider()

# ---------------- Execution ----------------

# ---- Aggregate Daily ----
if analysis_type == "Aggregate Daily":
    st.subheader("📅 Daily Aggregation (Precomputed View)")

    data = load_dataset("aggregated_time", "days")
    render_output(data)

# ---- Aggregate Sales By Time ----
elif analysis_type == "Aggregate Sales By Time":
    st.subheader("📦 Aggregated Sales By Time")

    data = load_dataset("aggregated_selling", "days" if freq == "D" else "months")
    render_output(data)

# ---- Sales Trend ----
elif analysis_type == "Sales Trend":
    st.subheader("📈 Sales Trend")

    data = load_dataset("trend", "days" if freq == "D" else "months")
    render_output(data)

# ---- Product Contribution ----
elif analysis_type == "Product Contribution":
    st.subheader("📊 Product Contribution")

    df_contrib = load_single_file("contribution", "product_contribution.csv")
    render_output(df_contrib)

# ---- Sales Period Detection ----
elif analysis_type == "Sales Period Detection":
    st.subheader("⚡ Sales Regimes")

    data = load_dataset("periods", "days" if freq == "D" else "months")
    render_output(data)

# ---- Sales Stability ----
elif analysis_type == "Sales Stability":
    st.subheader("📉 Sales Stability")

    df_stability = load_single_file("stability", "sales_stability.csv")
    render_output(df_stability)

# ---- Item Summary ----
elif analysis_type == "Item Summary":
    st.subheader("📌 Item Summary")

    if not item_id_input:
        st.warning("Enter item_id in sidebar")
    else:
        try:
            result = item_summary(df, item_id_input)
            st.dataframe(result)
        except Exception as e:
            st.error(str(e))