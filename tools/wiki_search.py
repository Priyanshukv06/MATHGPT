from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool

_wiki = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=1500)

def search_wikipedia(query: str) -> str:
    """Search Wikipedia and return a cleaned result."""
    try:
        result = _wiki.run(query)
        # keep printable ASCII + common unicode math chars
        return result.encode("utf-8", errors="replace").decode("utf-8")
    except Exception as e:
        return f"Wikipedia search failed: {e}"

wikipedia_tool = Tool(
    name="Wikipedia",
    func=search_wikipedia,
    description=(
        "Searches Wikipedia for factual information about math concepts, "
        "theorems, mathematicians, or any general knowledge topic. "
        "Input: a search query string."
    ),
)
