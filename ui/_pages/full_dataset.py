import streamlit as st

from shared.loaders import load_full_dataset
from components.table_view import render_table


def render():
    df = load_full_dataset()

    if df is None:
        st.stop()

    st.write(f"{len(df)} rows")

    render_table(df, "full_dataset")