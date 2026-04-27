import streamlit as st


def paginate(df, key: str):
    if df is None or len(df) == 0:
        return None

    total = len(df)

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        size = st.selectbox(
            "Page size",
            [20, 50, 100, 200],
            index=1,
            key=f"{key}_size"
        )

    pages = max((total - 1) // size + 1, 1)

    with col2:
        page = st.number_input(
            "Page",
            1,
            pages,
            1,
            key=f"{key}_page"
        )

    start = (page - 1) * size
    end = start + size

    with col3:
        st.caption(f"{start+1}-{min(end, total)} / {total}")

    return df.iloc[start:end]


def render_table(df, key: str):
    view = paginate(df, key)

    if view is not None:
        st.dataframe(view, use_container_width=True)