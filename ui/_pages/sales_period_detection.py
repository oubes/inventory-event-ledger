import streamlit as st

from shared.loaders import load_dataset
from components.table_view import render_table
from state.config import FREQ_MAP


def render():
    freq = st.selectbox("Frequency", ["D", "M"], key="period")

    data = load_dataset("periods", FREQ_MAP[freq])

    if data is None:
        st.stop()

    for k, v in data.items():
        st.subheader(k)
        render_table(v, f"period_{k}")