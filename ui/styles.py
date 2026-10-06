"""Small CSS layer on top of Streamlit's theme."""
import streamlit as st

CSS = """
<style>
.block-container { padding-top: 4.5rem; max-width: 1400px; }
h1 { font-size: 1.9rem !important; padding-top: 0 !important; }
h3 { font-size: 1.15rem !important; }
.step { display: inline-flex; align-items: center; gap: 8px; margin-right: 28px;
        color: #5B6472; font-size: 14px; }
.step b { width: 24px; height: 24px; border-radius: 50%; border: 1.5px solid #9AA3B2;
          display: inline-flex; align-items: center; justify-content: center; font-size: 12px; }
.step.active { color: #14181F; font-weight: 600; }
.step.active b { background: #1F4FD8; border-color: #1F4FD8; color: #fff; }
.tag { font-size: 12px; font-weight: 600; padding: 3px 8px; border-radius: 4px;
       background: #E8EDFB; color: #173A9F; }
</style>
"""


def apply_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)