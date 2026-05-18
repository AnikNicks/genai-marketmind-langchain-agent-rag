#Live open-web interface engine.

import logging
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

logger = logging.getLogger(__name__)

@tool
def live_web_search(query: str) -> str:
    """Use this tool to search the live web for recent 2026 updates, breaking market trends,
    stock variations, macroeconomic news, and competitor actions."""
    try:
        search = DuckDuckGoSearchRun()
        return search.run(query)
    except Exception as e:
        return f"Web search interface failed: {str(e)}"