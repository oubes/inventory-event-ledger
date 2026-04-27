import streamlit as st

from shared.loaders import load_single_file
from components.table_view import render_table


def render():
    df = load_single_file("stability", "sales_stability.csv")

    if df is None:
        st.stop()

    render_table(df, "stability")