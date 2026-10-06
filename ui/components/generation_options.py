import streamlit as st

from config import DEFAULT_TECHNIQUES, DEFAULT_TEST_TYPES, TECHNIQUES, TEST_TYPES

def render_generation_options() -> tuple[list[str], list[str]]:
    """Two multi-select dropdowns. Returns (techniques, test_types)."""
    left, right = st.columns(2)
    techniques = left.multiselect("Test design techniques", TECHNIQUES, default=DEFAULT_TECHNIQUES)
    test_types = right.multiselect("Types of testing", TEST_TYPES, default=DEFAULT_TEST_TYPES)
    return techniques, test_types


def render_generate_bar(criteria_count: int) -> bool:
    """Criteria counter plus the Generate button. Returns True when clicked."""
    left, right = st.columns([3, 1])
    left.caption(f"{criteria_count} acceptance criteria detected")
    return right.button("Generate test cases", type="primary", use_container_width=True)