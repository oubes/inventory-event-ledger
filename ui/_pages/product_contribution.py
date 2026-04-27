import streamlit as st
import pandas as pd
import plotly.express as px

from shared.loaders import load_single_file
from components.table_view import render_table


def render():
    df = load_single_file("contribution", "product_contribution.csv")

    if not isinstance(df, pd.DataFrame) or df.empty:
        st.stop()

    render_table(df, "contrib")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if not numeric_cols:
        st.info("No numeric data for visualization")
        return

    value_col = None

    for col in numeric_cols:
        max_val = df[col].max()
        if max_val <= 1.0 or max_val <= 100:
            value_col = col
            break

    if value_col is None:
        value_col = numeric_cols[0]

    plot_df = df.copy()

    if plot_df[value_col].max() <= 1:
        plot_df[value_col] = plot_df[value_col] * 100

    label_col = plot_df.columns[0]

    plot_df = plot_df.sort_values(value_col, ascending=False)

    # ---------------- CLEAN UI ENHANCEMENT ----------------
    fig = px.pie(
        plot_df,
        names=label_col,
        values=value_col,
        hole=0.55,
        title="Product Contribution",
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Value: %{value:.2f}%<extra></extra>"
    )

    fig.update_layout(
        showlegend=True,
        legend_title_text="Products",
        margin=dict(l=20, r=20, t=40, b=20),
        title_x=0.5
    )

    st.plotly_chart(fig, use_container_width=True)