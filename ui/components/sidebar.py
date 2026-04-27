import streamlit as st


def render_sidebar():
    st.sidebar.header("Controls")

    return st.sidebar.selectbox(
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