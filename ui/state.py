"""Session state helpers. All reads and writes of st.session_state live here."""
from dataclasses import replace

import streamlit as st

from models import GenerationRequest, TestCase


def init_state() -> None:
    st.session_state.setdefault("test_cases", [])
    st.session_state.setdefault("last_request", None)


def set_test_cases(cases: list[TestCase]) -> None:
    """Store new results and drop edits/selections from the previous run."""
    for key in [k for k in st.session_state if k.startswith(("steps_", "pick_"))]:
        del st.session_state[key]
    st.session_state["test_cases"] = cases


def current_test_cases(only_selected: bool = False) -> list[TestCase]:
    """Return test cases with any step edits applied."""
    result = []
    for case in st.session_state["test_cases"]:
        if only_selected and not st.session_state.get(f"pick_{case.id}", True):
            continue
        steps = st.session_state.get(f"steps_{case.id}", case.steps)
        result.append(replace(case, steps=steps))
    return result


def save_request(request: GenerationRequest) -> None:
    st.session_state["last_request"] = request


def get_request() -> GenerationRequest | None:
    return st.session_state["last_request"]