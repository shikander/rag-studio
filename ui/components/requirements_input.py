import streamlit as st

from config import INPUT_SOURCES, SAMPLE_CRITERIA


def _paste_tab() -> str:
    return st.text_area(
        "Story and acceptance criteria", value=SAMPLE_CRITERIA, height=230, key="criteria_text"
    )


def _jira_tab() -> None:
    st.text_input("Jira issue key", placeholder="[PROJECT-123]")
    st.button("Fetch from Jira")
    st.caption("Jira connector coming soon.")


def _confluence_tab() -> None:
    st.text_input("Confluence page URL", placeholder="[PAGE URL]")
    st.button("Fetch from Confluence")
    st.caption("Confluence connector coming soon.")


def _upload_tab() -> str:
    file = st.file_uploader("Requirements file", type=["txt", "md"])
    return file.getvalue().decode("utf-8") if file else ""


def render_requirements_input() -> str:
    """Show the source tabs and return the criteria text to use."""
    paste, jira, confluence, upload = st.tabs(INPUT_SOURCES)
    with paste:
        pasted = _paste_tab()
    with jira:
        _jira_tab()
    with confluence:
        _confluence_tab()
    with upload:
        uploaded = _upload_tab()
    return uploaded or pasted