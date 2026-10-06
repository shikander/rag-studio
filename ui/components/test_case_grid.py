import csv
import io
from html import escape

import streamlit as st

from config import GRID_COLUMNS
from models import TestCase

WIDTHS = [width for _, width in GRID_COLUMNS]

def _to_csv(cases: list[TestCase]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["ID", "Criterion", "Type", "Scenario", "Steps", "Data", "Expected"])
    for c in cases:
        writer.writerow([c.id, c.criterion, c.test_type, c.scenario, c.steps, c.data, c.expected])
    return buffer.getvalue()

def _render_header_row() -> None:
    for column, (title, _) in zip(st.columns(WIDTHS), GRID_COLUMNS):
        column.caption(title.upper())

def _render_row(case: TestCase) -> None:
    pick, case_id, scenario, steps, data, expected = st.columns(WIDTHS)
    pick.checkbox(f"Include {case.id}", value=True, key=f"pick_{case.id}", label_visibility="collapsed")
    case_id.markdown(f"`{case.id}`")
    scenario.markdown(
        f'<span class="tag">{case.criterion} {case.test_type}</span><br>{escape(case.scenario)}',
        unsafe_allow_html=True,
    )
    steps.text_area(
        f"Steps {case.id}", value=case.steps, height=120, key=f"steps_{case.id}",
        label_visibility="collapsed",
    )
    data.markdown(case.data.replace("\n", "  \n"))
    expected.write(case.expected)


def _render_title_and_actions(cases: list[TestCase], criteria_count: int) -> str | None:
    """Title on the left, three action buttons on the right. Returns the clicked action."""
    action = None
    title, buttons = st.columns([3, 3])
    title.subheader("Generated test cases")
    title.caption(f"{len(cases)} test cases from {criteria_count} criteria. Edit any step before continuing.")
    export, regenerate, proceed = buttons.columns([1, 1, 1.4])
    export.download_button("Export CSV", _to_csv(cases), "test_cases.csv", "text/csv")
    if regenerate.button("Regenerate"):
        action = "regenerate"
    if proceed.button("Continue to Playwright", type="primary"):
        action = "continue"
    return action


def render_test_case_grid(cases: list[TestCase], criteria_count: int) -> str | None:
    """Show the grid. Returns 'regenerate', 'continue' or None."""
    with st.container(border=True):
        action = _render_title_and_actions(cases, criteria_count)
        st.divider()
        _render_header_row()
        for case in cases:
            _render_row(case)
    return action