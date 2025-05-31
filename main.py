# # main.py
# import os
# from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# # Import configurations and the compiled agent graph
# import config
# from agent_graph import compiled_agent_graph, AgentState # Import the compiled graph

# def run_agent_interaction(query: str, recursion_limit=15):
#     """
#     Runs a query through the agent and prints the interaction flow.
#     Prompt Engineering Point 3: The user's query itself.
#     Clear, specific queries yield better results.
#     """
#     if not config.GROQ_API_KEY:
#         print("🔴 ERROR: GROQ_API_KEY is not set. Please set it in your environment or config.py.")
#         return

#     print(f"\n🚀 Starting Agent Interaction for Query: '{query}'")
#     print(f"Using Groq model: {config.GROQ_MODEL_NAME}, Temperature: {config.LLM_TEMPERATURE}")

#     # Initial state for the graph with the user's query
#     initial_state: AgentState = {"messages": [HumanMessage(content=query)]}

#     event_count = 0
#     final_answer_delivered = False

#     # Stream events to observe the flow of execution through the graph.
#     # A recursion_limit is crucial to prevent potential infinite loops.
#     for event in compiled_agent_graph.stream(initial_state, {"recursion_limit": recursion_limit}):
#         event_count += 1
#         print(f"\n--- Event {event_count} ---")

#         for node_name, output_data in event.items(): # Each event is a dict with node_name: output
#             print(f"Node Executed: {node_name}")
#             if isinstance(output_data, dict) and "messages" in output_data:
#                 # This is output from 'agent' or 'tools' node
#                 print("Messages in this step's output:")
#                 for msg in output_data["messages"]:
#                     print(f"  {msg.pretty_repr()}") # LangChain's pretty representation
#             else:
#                 # This typically happens for the __end__ node or other non-message outputs
#                 print(f"  Output Data: {output_data}")

#             # Check for the end of the graph execution
#             if node_name == "__end__":
#                 print("\n🏁 Agent Execution Finished.")
#                 # The final state is available in the event dictionary under the key "__end__"
#                 final_state_messages = event.get("__end__", {}).get("messages", [])
#                 if final_state_messages:
#                     last_ai_message_content = None
#                     # Iterate backwards to find the last direct AI response
#                     for m in reversed(final_state_messages):
#                         if isinstance(m, AIMessage) and not m.tool_calls:
#                             last_ai_message_content = m.content
#                             break
#                     if last_ai_message_content:
#                         print(f"\n✅ Final Agent Answer:\n{last_ai_message_content}")
#                         final_answer_delivered = True
#                     else:
#                         print("⚠️ No direct final AIMessage found. The conversation might have ended after a tool call without further synthesis by the agent.")
#                 else:
#                      print("⚠️ No messages found in the final __end__ state.")
#                 return # Exit the function once the graph ends

#     if not final_answer_delivered:
#          print("\n⚠️ Agent interaction concluded without a clearly identified final answer via streaming. Check logs.")



# # main.py - temporary test
# from tools_definition import calculator

# if __name__ == "__main__":
#     print("Testing calculator directly...")
#     output = calculator("2025 - 1624")
#     print(f"Calculator raw output: '{output}'")
#     output_simple = calculator("5 + 10")
#     print(f"Calculator simple output: '{output_simple}'")





# # if __name__ == "__main__":
# #     # Ensure the API key is handled by config.py, which checks environment variables.
# #     if not config.GROQ_API_KEY:
# #         print("🔴 FATAL ERROR: GROQ_API_KEY environment variable not set.")
# #         print("Please set it before running the script. Example for Linux/macOS:")
# #         print("  export GROQ_API_KEY='your_gsk_your_key_here'")
# #         print("Example for Windows (PowerShell):")
# #         print("  $env:GROQ_API_KEY='your_gsk_your_key_here'")
# #         print("Alternatively, set it directly in config.py (not recommended for production).")
# #     else:
# #         print(f"✅ Groq API Key loaded. Using model: {config.GROQ_MODEL_NAME}")
# #         print("---")
# #         print("🚨 SAFETY WARNINGS 🚨")
# #         print("1. The 'calculator' tool uses `eval()`, which is unsafe with untrusted input.")
# #         print("2. The 'python_code_executor' tool uses `exec()`, which is EXTREMELY DANGEROUS and can execute arbitrary code. It is NOT SANDBOXED.")
# #         print("   >>> USE THESE TOOLS WITH EXTREME CAUTION AND ONLY WITH TRUSTED INPUTS during development. <<<")
# #         print("---\n")

# #         # --- Example Queries ---
# #         # Simple interaction
# #         # run_agent_interaction("Hello! Can you tell me a fun fact about the Llama animal?")

# #         # Requires web search and then calculator
# #         run_agent_interaction("Search for the current price of gold per ounce in USD. Then, tell me how much 3.5 ounces would cost.")

# #         # Requires calculator
# #         # run_agent_interaction("What is ((18 / 3) * 7) + 13 - 5 ?")

# #         # DANGEROUS: Requires Python code execution. Only run if you understand the risk.
# #         # run_agent_interaction("Execute this Python code and tell me the output: numbers = [10, 20, 30, 5]; result = sum(numbers) / len(numbers)")

# #         # Requires web search and then summarization (using the document_summarizer tool)
# #         run_agent_interaction("Find an article about the benefits of learning a new language and then summarize its key points for me. Use the original user query as context for the summary.")
# #         # Note for the above: The agent needs to:
# #         # 1. Use web_search to find an article.
# #         # 2. Extract text from one of the results (LLM might need to decide which one).
# #         # 3. Call document_summarizer with that text and the original query context.

# #         # Direct summarization test for the tool (if you provide the text directly)
# #         # run_agent_interaction("Please summarize this text for me using the summarizer tool: 'LangGraph is a powerful library for building stateful, multi-actor applications with large language models. It allows developers to create complex agent runtimes and coordinate multiple chains of computation in a cyclical and robust manner. It is part of the LangChain ecosystem.' My original question was about understanding LangGraph.")

# main.py - temporary direct tool test
from tools_definition import calculator, ALL_TOOLS # Make sure ALL_TOOLS is imported if agent_system_message_content needs it below, or just calculator
# from agent_graph import agent_system_message_content # If you want to print this too

if __name__ == "__main__":
    print("--- Direct Calculator Test ---")

    expression1 = "5 + 10"
    print(f"Testing with expression: '{expression1}'")
    output1 = calculator(expression1)
    print(f"Output for '{expression1}': >>>{output1}<<< (Type: {type(output1)})")
    print("-" * 30)

    expression2 = "2025 - 1624"
    print(f"Testing with expression: '{expression2}'")
    output2 = calculator(expression2)
    print(f"Output for '{expression2}': >>>{output2}<<< (Type: {type(output2)})")
    print("-" * 30)

    # Test an expression that would cause an error within calculator's eval
    expression3 = "1 / 0"
    print(f"Testing with expression: '{expression3}' (expected internal eval error)")
    output3 = calculator(expression3)
    print(f"Output for '{expression3}': >>>{output3}<<< (Type: {type(output3)})")
    print("-" * 30)

    # Test an expression with invalid characters
    expression4 = "hello + world"
    print(f"Testing with expression: '{expression4}' (expected invalid char error)")
    output4 = calculator(expression4)
    print(f"Output for '{expression4}': >>>{output4}<<< (Type: {type(output4)})")
    print("-" * 30)

    # If you have the system message defined and want to see it
    # This part requires agent_system_message_content to be importable or defined
    # from agent_graph import agent_system_message_content
    # print("\n--- Agent System Message Content (for reference) ---")
    # print(agent_system_message_content)