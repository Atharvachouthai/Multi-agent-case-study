# tools_definition.py
import json
from typing import Optional

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
import config

@tool
def web_search(query: str) -> str:
    """
    Searches the web for the given query using DuckDuckGo to find current information, news, facts, or general knowledge.
    Returns a JSON string with a list of search results, each containing 'title', 'href', and 'body'.
    Use this when you need up-to-date information or to answer questions about topics not in your inherent knowledge.
    For example, if asked 'What is the weather in London?' or 'Who won the latest F1 race?', use this tool.
    Choose concise and effective search queries.
    """
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = [
                {"title": r.get("title"), "href": r.get("href"), "body": r.get("body")}
                for r in ddgs.text(query, max_results=3)
            ]
            return json.dumps(results) if results else "No results found."
    except ImportError:
        return "Error: duckduckgo-search library not installed. Please run 'pip install duckduckgo-search'."
    except Exception as e:
        return f"Error in web_search: {str(e)}"

@tool
def calculator(expression: str) -> str:
    """
    Calculates the result of a mathematical expression.
    Input MUST be a valid mathematical expression string (e.g., "2 + 2 * 5", "(100-20)/5").
    Only supports basic arithmetic operations: +, -, *, /, parentheses.
    Use this for any math calculation required to answer the user.
    For example, if asked 'If an item costs $10 and sales tax is 10%, what is the tax amount?',
    you might first determine the tax is 10 * 0.10 and then call this tool with expression='10 * 0.10'.
    """
    try:
        allowed_chars = "0123456789+-*/(). "
        if not all(char in allowed_chars for char in expression):
            error_msg = f"Error: Invalid characters in expression '{expression}'. Only numbers and basic math operators/parentheses are allowed."
            return error_msg
        result = eval(expression)
        str_result = str(result)
        return str_result
    except Exception as e:
        error_msg = f"Error in calculator for expression '{expression}': {str(e)}"
        return error_msg

@tool
def python_code_executor(code: str) -> str:
    """
    Executes a given string of Python code. The code MUST be safe and simple.
    The code should assign its main output to a variable named 'result' to be captured.
    Example: To find the length of a list, use code like 'my_list = [1,2,3]; result = len(my_list)'.
    Use this tool when explicitly asked to run Python code or if a task is best solved by a short Python script (e.g., complex text manipulation not covered by other tools).
    WARNING: Executes arbitrary code. Ensure the code is simple and safe. Do NOT use for file system access or network calls.
    """
    try:
        local_scope = {}
        restricted_builtins = {
            "print": print, "len": len, "str": str, "int": int, "float": float, "list": list,
            "dict": dict, "sum": sum, "min": min, "max": max, "range": range, "abs": abs,
            "round": round, "True": True, "False": False, "None": None,
        }
        exec(code, {"__builtins__": restricted_builtins}, local_scope)
        captured_result = local_scope.get("result", "Code executed. No 'result' variable found or assigned by the code.")
        try:
            return json.dumps({"execution_status": "success", "output": captured_result})
        except TypeError:
            return json.dumps({"execution_status": "success", "output": str(captured_result)})
    except Exception as e:
        return json.dumps({"execution_status": "error", "output": str(e)})

@tool
def document_summarizer(text_content: str, query_context: Optional[str] = None) -> str:
    """
    Summarizes the provided 'text_content'.
    If 'query_context' (e.g., the original user question or topic of interest) is provided, the summary will be tailored to be relevant to it.
    Use this tool when you have a long piece of text that needs to be condensed, for example, the content of a web article found by web_search.
    Example: If web_search returns a long article and the user wants key points, pass the article's text here.
    """
    if not text_content:
        return "Error: No text content provided to summarize."
    if not config.GROQ_API_KEY:
        return "Error: GROQ_API_KEY not configured for summarizer tool."

    try:
        summarizer_llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL_NAME,
            temperature=config.LLM_TEMPERATURE
        )
        system_prompt_message = "You are an expert at summarizing text. Provide a clear, concise, and neutral summary of the provided content. Focus on the main facts and key takeaways. Do not add any preamble like 'Here is the summary:' or opinions unless the text explicitly contains them."
        if query_context:
            system_prompt_message += f"\nThe summary should specifically highlight information relevant to this context or question: '{query_context}'"
        
        messages = [
            HumanMessage(content=system_prompt_message),
            HumanMessage(content=f"Please summarize this text:\n\nTEXT_START\n{text_content}\nTEXT_END")
        ]
        response = summarizer_llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error during summarization LLM call: {str(e)}"

ALL_TOOLS = [web_search, calculator, python_code_executor, document_summarizer]