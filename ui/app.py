"""RAG Studio UI entry point. Run with:  streamlit run app.py"""
import streamlit as st

import state
from api_client import ApiError, generate_test_cases
from components.generation_options import render_generate_bar, render_generation_options
from components.header import render_page_header, render_stepper
from components.requirements_input import render_requirements_input
from components.run_settings import render_run_settings
from components.sidebar import render_sidebar
from components.test_case_grid import render_test_case_grid
from config import APP_TITLE
from criteria import count_criteria
from models import GenerationRequest
from styles import apply_styles

CURRENT_STEP = 1


def setup_page() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    apply_styles()
    state.init_state()


def validate_inputs(criteria_count: int, techniques: list[str], test_types: list[str]) -> str | None:
    if criteria_count == 0:
        return "No acceptance criteria found. Start each one with AC1:, AC2: and so on."
    if not techniques or not test_types:
        return "Select at least one technique and one type of testing."
    return None


def run_generation(request: GenerationRequest) -> bool:
    """Call the API and store the result. Returns False (and shows an error) on failure."""
    with st.spinner("Generating test cases..."):
        try:
            cases = generate_test_cases(request)
        except ApiError as error:
            st.error(str(error))
            return False
        state.set_test_cases(cases)
        state.save_request(request)
    return True


def handle_generate_click(criteria: str, techniques, test_types, sources, model) -> None:
    error = validate_inputs(count_criteria(criteria), techniques, test_types)
    if error:
        st.warning(error)
        return
    run_generation(GenerationRequest(criteria, techniques, test_types, sources, model))


def handle_grid_action(action: str | None) -> None:
    if action == "regenerate":
        if run_generation(state.get_request()):
            st.rerun()
    elif action == "continue":
        selected = state.current_test_cases(only_selected=True)
        st.success(f"{len(selected)} test cases ready. The Playwright page is the next screen to build.")


def render_input_section() -> tuple:
    """Left column: input, options and the Generate button."""
    with st.container(border=True):
        criteria = render_requirements_input()
        techniques, test_types = render_generation_options()
        clicked = render_generate_bar(count_criteria(criteria))
    return criteria, techniques, test_types, clicked


def render_results_section() -> None:
    cases = state.current_test_cases()
    if not cases:
        return
    criteria_count = len({case.criterion for case in cases})
    handle_grid_action(render_test_case_grid(cases, criteria_count))


def main() -> None:
    setup_page()
    render_sidebar(CURRENT_STEP)
    render_page_header("[PROJECT NAME] / New run", "Requirements and test cases")
    render_stepper(CURRENT_STEP)

    left, right = st.columns([2.2, 1])
    with left:
        criteria, techniques, test_types, clicked = render_input_section()
    with right:
        sources, model = render_run_settings()

    if clicked:
        handle_generate_click(criteria, techniques, test_types, sources, model)
    render_results_section()


main()