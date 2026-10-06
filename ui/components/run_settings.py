import streamlit as st

from config import CONTEXT_SOURCES, MODELS


def render_run_settings() -> tuple[list[str], str]:
    """Returns (selected context sources, model)."""
    with st.container(border=True):
        st.subheader("Run settings")
        st.markdown("**Retrieve context from**")
        sources = [name for name in CONTEXT_SOURCES if st.checkbox(name, value=True)]
        model = st.selectbox("Test case model", MODELS)
    return sources, model