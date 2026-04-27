import streamlit as st

from shared.loaders import load_dataset
from components.table_view import render_table


def render():
    data = load_dataset("aggregated_time", "days")

    if data is None:
        st.stop()

    for k, v in data.items():
        st.subheader(k)
        render_table(v, f"daily_{k}")