# agent_graph.py
import operator
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

import config
from tools_definition import ALL_TOOLS

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

agent_system_message_content = f"""You are "Cognito", a highly capable multi-tool AI assistant.
Your goal is to accurately understand complex user requests, break them down into logical subgoals if necessary,
and utilize available tools effectively to gather information or perform actions.
After using tools, synthesize the information clearly to provide a comprehensive final answer.

Think step-by-step. Here's a general approach you should take:
1. Understand the user's full request.
2. If it's a simple request you can answer directly, do so.
3. If it's complex or requires specific information/actions:
    a. Identify the core task(s) or question(s).
    b. Check if any of your available tools can help.
    c. If a tool is needed, formulate the precise input for that tool and call it.
    d. If multiple tools are needed, plan their use in a logical sequence.
    e. Use the output from tools to inform your next step or to formulate your final answer.
4. If a tool fails or returns an error, acknowledge it and try to proceed if possible, or inform the user if you cannot complete the request.

Example thought process for tool selection:
- User asks: "What's the capital of France and what's 25 * 76?"
  Your thought process:
    - Task 1: Find capital of France. This is a factual lookup. The 'web_search' tool is best. Query: "capital of France".
    - Task 2: Calculate 25 * 76. This is a math problem. The 'calculator' tool is best. Expression: "25 * 76".
    - After getting results from both tools, I will combine them into a final answer.

- User asks: "Summarize the main points of the Wikipedia article on photosynthesis."
  Your thought process:
    - Task 1: Get the content of the Wikipedia article. 'web_search' tool with query "Wikipedia photosynthesis".
    - Task 2: Once I have the text from the search result, if it's long, I should use the 'document_summarizer' tool with the article text.

Available tools are: {', '.join([tool.name for tool in ALL_TOOLS])}.
Carefully read their descriptions (which you will receive) to understand their purpose and how to use them.
Always aim to be helpful and accurate.
"""

if not config.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment or config.py. Please set it.")

main_llm = ChatGroq(
    groq_api_key=config.GROQ_API_KEY,
    model_name=config.GROQ_MODEL_NAME,
    temperature=config.LLM_TEMPERATURE
)

llm_with_tools = main_llm.bind_tools(ALL_TOOLS)

def agent_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(ALL_TOOLS)

def router_node(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    else:
        return END

def create_agent_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        router_node,
        {"tools": "tools", END: END}
    )
    workflow.add_edge("tools", "agent")
    app = workflow.compile()
    return app

compiled_agent_graph = create_agent_graph()