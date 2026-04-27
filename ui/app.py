import streamlit as st

from components.sidebar import render_sidebar

from _pages import (
    full_dataset,
    aggregate_daily,
    aggregate_sales_by_time,
    sales_trend,
    product_contribution,
    sales_period_detection,
    sales_stability
)

st.set_page_config(page_title="Sales Analytics Engine", layout="wide")
st.title("Sales Analytics Engine")

page = render_sidebar()


if page == "Full Dataset":
    full_dataset.render()

elif page == "Aggregate Daily":
    aggregate_daily.render()

elif page == "Aggregate Sales By Time":
    aggregate_sales_by_time.render()

elif page == "Sales Trend":
    sales_trend.render()

elif page == "Product Contribution":
    product_contribution.render()

elif page == "Sales Period Detection":
    sales_period_detection.render()

elif page == "Sales Stability":
    sales_stability.render()