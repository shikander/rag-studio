class NoCriteriaFoundError(ValueError):
    """The input text has no lines like 'AC1: ...'."""


class RunNotFoundError(LookupError):
    """No run exists with the given id."""


class LlmNotConfiguredError(RuntimeError):
    """The LLM generator was selected but no API key is set."""


class LlmError(RuntimeError):
    """The LLM provider call failed. The message is safe to show to the user."""


class InvalidLlmOutputError(LlmError):
    """The model replied, but not with usable JSON."""