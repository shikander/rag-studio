import streamlit as st

from config import WORKFLOW_STEPS


def render_page_header(breadcrumb: str, title: str) -> None:
    left, right = st.columns([5, 1])
    with left:
        st.caption(breadcrumb)
        st.title(title)
    right.button("Run history")


def render_stepper(current_step: int) -> None:
    items = []
    for number, label in enumerate(WORKFLOW_STEPS, start=1):
        css = "step active" if number == current_step else "step"
        items.append(f'<span class="{css}"><b>{number}</b>{label}</span>')
    st.markdown("".join(items), unsafe_allow_html=True)