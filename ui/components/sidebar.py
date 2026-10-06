import streamlit as st

from config import APP_TITLE, KNOWLEDGE_PAGES, WORKFLOW_STEPS

def _render_workflow(current_step: int) -> None:
    st.caption("WORKFLOW")
    for number, label in enumerate(WORKFLOW_STEPS, start=1):
        text = f"{number}. {label}"
        st.markdown(f"**{text}**" if number == current_step else text)


def _render_knowledge() -> None:
    st.caption("KNOWLEDGE")
    for page in KNOWLEDGE_PAGES:
        st.markdown(page)


def render_sidebar(current_step: int) -> None:
    with st.sidebar:
        st.header(APP_TITLE)
        _render_workflow(current_step)
        st.divider()
        _render_knowledge()