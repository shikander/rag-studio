"""Static settings and option lists for the UI."""

APP_TITLE = "RAG Studio"

WORKFLOW_STEPS = ["Requirements and test cases", "Playwright", "Validate"]

KNOWLEDGE_PAGES = ["Documents", "App context (POMs)", "Evaluation", "Settings"]

INPUT_SOURCES = ["Paste", "Jira", "Confluence", "Upload file"]

TECHNIQUES = [
    "Boundary value analysis",
    "Equivalence partitioning",
    "Decision table",
    "State transition",
    "Error guessing",
    "Pairwise combinations",
]

DEFAULT_TECHNIQUES = ["Boundary value analysis", "Equivalence partitioning"]

TEST_TYPES = [
    "Functional",
    "Negative",
    "Performance",
    "Security",
    "Accessibility",
    "Usability",
    "Compatibility",
]
DEFAULT_TEST_TYPES = ["Functional"]

CONTEXT_SOURCES = ["Related requirements", "Existing tests", "App context (POMs, selectors)"]

MODELS = ["Fast and cheap (OpenRouter)", "Strong coder (OpenRouter)"]

SAMPLE_CRITERIA = """Story: As a registered user, I want to log in so that I can see my dashboard.

AC1: Given I am on /login, when I enter valid credentials, then I am redirected to /dashboard.
AC2: Given I am on /login, when I enter a wrong password, then I see an inline error and stay on /login.
AC3: Given I have failed 5 times, when I try again, then the account is locked for 15 minutes."""

# Test case grid: (header, relative width)
GRID_COLUMNS = [
    ("", 0.5),
    ("Test case ID", 1),
    ("Description / scenario", 2.2),
    ("Test steps", 3),
    ("Test data", 2.2),
    ("Expected results", 2.6),
]