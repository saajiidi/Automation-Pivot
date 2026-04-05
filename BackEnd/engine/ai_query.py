import pandas as pd
from typing import Optional, Tuple


AI_DISABLED_MESSAGE = (
    "AI assistant is currently disabled. The deprecated Gemini integration "
    "has been removed from this app."
)


def query_app_data(
    prompt: str, df: pd.DataFrame, api_key: str
) -> Tuple[str, Optional[pd.DataFrame]]:
    """
    Placeholder response after removing the deprecated AI provider integration.
    """
    if df is None or df.empty:
        return "The dataset is empty. I cannot search an empty database.", None

    return AI_DISABLED_MESSAGE, None


def generic_chat(prompt: str, api_key: str, history: list) -> str:
    """Placeholder chat response after removing the deprecated AI provider."""
    return AI_DISABLED_MESSAGE
