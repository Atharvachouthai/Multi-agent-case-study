# streamlit_app.py
import streamlit as st
import json
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

try:
    import config
    from agent_graph import compiled_agent_graph, AgentState, agent_system_message_content
except ImportError as e:
    st.error(f"Failed to import agent components. Ensure all .py files (config.py, tools_definition.py, agent_graph.py) are correct and in the same directory. Error: {e}")
    st.stop()

st.set_page_config(page_title="🧠 Multi-Tool LLM Agent", layout="wide")
st.title("🧠 Multi-Tool LLM Agent with Groq & LLaMA")

if not config.GROQ_API_KEY:
    st.warning("""
        **Groq API Key Not Found!** 🔑
        Please set the `GROQ_API_KEY` environment variable to use this application.
    """)
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Existing Chat Messages from Session State (MODIFIED) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        elif message["role"] == "assistant":
            # Display textual content first, if any
            if message["content"]:
                 st.markdown(message["content"])
            # If this assistant message had tool calls, display them from history
            if message.get("tool_calls"):
                st.markdown("---") # Add a separator
                st.markdown("**🛠️ Tools Planned in this Step:**")
                for tc_history in message["tool_calls"]:
                    st.markdown(f"- **Tool:** `{tc_history['name']}`")
                    st.markdown(f"  - **Arguments:**")
                    st.json(tc_history['args']) # Display arguments as JSON for clarity
                st.markdown("---")

        # We don't display "tool" role messages from history in the main chat to keep it clean,
        # as their results are incorporated into subsequent assistant messages.
        # The live st.status box shows "Tool Executed: <tool_name>"


# --- User Input and Agent Interaction Logic (remains the same as the last "cleaned" version) ---
if prompt := st.chat_input("Ask the agent anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("🤖 Agent is working...", expanded=True) as status_box:
            final_llm_answer_content = ""
            tool_calls_for_this_turn = [] # Track tool calls planned in this specific turn

            temp_history_for_graph = []
            for msg_data in st.session_state.messages:
                if msg_data["role"] == "user":
                    temp_history_for_graph.append(HumanMessage(content=msg_data["content"]))
                elif msg_data["role"] == "assistant":
                    ai_content = msg_data.get("content", "")
                    tool_calls_from_history = msg_data.get("tool_calls")
                    valid_tool_calls = []
                    if isinstance(tool_calls_from_history, list):
                        valid_tool_calls = tool_calls_from_history
                    temp_history_for_graph.append(
                        AIMessage(content=ai_content, tool_calls=valid_tool_calls)
                    )
                elif msg_data["role"] == "tool":
                    temp_history_for_graph.append(
                        ToolMessage(
                            content=msg_data["content"],
                            tool_call_id=msg_data["tool_call_id"],
                            name=msg_data.get("tool_name", "unknown_tool")
                        )
                    )
            
            graph_messages_history = [SystemMessage(content=agent_system_message_content)] + temp_history_for_graph
            initial_state: AgentState = {"messages": graph_messages_history}
            current_tool_call_id_to_name_map = {}

            try:
                for event in compiled_agent_graph.stream(initial_state, {"recursion_limit": 15}):
                    for node_name, output_data in event.items():
                        if node_name != "__end__":
                             status_box.write(f"⚙️ Processing: '{node_name}'...")

                        if isinstance(output_data, dict) and "messages" in output_data:
                            for msg_obj in output_data["messages"]:
                                if isinstance(msg_obj, AIMessage):
                                    if msg_obj.tool_calls:
                                        status_box.write(f"🧠 LLM plans to use tool(s):")
                                        for tc in msg_obj.tool_calls:
                                            status_box.markdown(f"  - Tool: `{tc['name']}`, Args: `{json.dumps(tc['args'])}`")
                                            current_tool_call_id_to_name_map[tc['id']] = tc['name']
                                            tool_calls_for_this_turn.append(tc)
                                        if msg_obj.content:
                                            status_box.write(f"🗣️ LLM says: _{msg_obj.content}_")

                                elif isinstance(msg_obj, ToolMessage):
                                    tool_name_from_message = msg_obj.name or current_tool_call_id_to_name_map.get(msg_obj.tool_call_id, "unknown_tool")
                                    status_box.write(f"🛠️ **Tool Executed:** `{tool_name_from_message}`. Agent is processing the result...")
                                    
                                    already_logged = False
                                    for logged_msg in st.session_state.messages:
                                        if logged_msg.get("role") == "tool" and logged_msg.get("tool_call_id") == msg_obj.tool_call_id:
                                            already_logged = True
                                            break
                                    if not already_logged:
                                        st.session_state.messages.append({
                                            "role": "tool",
                                            "content": msg_obj.content, 
                                            "tool_call_id": msg_obj.tool_call_id,
                                            "tool_name": tool_name_from_message
                                        })
                                    pass

                        if node_name == "__end__":
                            status_box.update(label="✔️ Agent: Task complete!", state="complete", expanded=False)
                            break 
                    if node_name == "__end__":
                        break 
                
                final_graph_state_after_turn = compiled_agent_graph.invoke(initial_state, {"recursion_limit":15})
                
                if final_graph_state_after_turn and final_graph_state_after_turn.get("messages"):
                    last_msg_in_turn = final_graph_state_after_turn["messages"][-1]
                    if isinstance(last_msg_in_turn, AIMessage) and not last_msg_in_turn.tool_calls:
                        final_llm_answer_content = last_msg_in_turn.content
                    elif isinstance(last_msg_in_turn, AIMessage) and last_msg_in_turn.content:
                        if not final_llm_answer_content: 
                             final_llm_answer_content = last_msg_in_turn.content
                
            except Exception as e:
                st.error(f"An error occurred during agent execution: {str(e)}")
                status_box.update(label="❌ Agent: Error!", state="error", expanded=True)
                final_llm_answer_content = "I encountered an error and couldn't complete your request."

            assistant_message_to_store = {}
            if final_llm_answer_content:
                st.markdown(final_llm_answer_content) 
                assistant_message_to_store = {"role": "assistant", "content": final_llm_answer_content}
            elif tool_calls_for_this_turn: 
                final_content_for_tool_planning_turn = ""
                temp_ai_content_with_tool_call = ""
                
                # Find the AI message content that accompanied these tool_calls_for_this_turn
                # This requires looking at the messages produced in the current turn's stream.
                # A simple way is to check if the last message in the graph state for *this turn* had these tool calls and content.
                if final_graph_state_after_turn and final_graph_state_after_turn.get("messages"):
                    last_message_obj = final_graph_state_after_turn["messages"][-1]
                    # Check if this last message corresponds to the current tool planning phase
                    if isinstance(last_message_obj, AIMessage) and last_message_obj.tool_calls:
                        # Compare tool call IDs to be more precise
                        planned_ids_this_turn = {tc['id'] for tc in tool_calls_for_this_turn}
                        last_msg_tc_ids = {tc['id'] for tc in last_message_obj.tool_calls}
                        if planned_ids_this_turn == last_msg_tc_ids and last_message_obj.content:
                            temp_ai_content_with_tool_call = last_message_obj.content

                if temp_ai_content_with_tool_call:
                     final_content_for_tool_planning_turn = temp_ai_content_with_tool_call
                else:
                    final_content_for_tool_planning_turn = "Okay, I will use my tools for that."


                st.markdown(final_content_for_tool_planning_turn)
                assistant_message_to_store = {
                    "role": "assistant",
                    "content": final_content_for_tool_planning_turn,
                    "tool_calls": tool_calls_for_this_turn
                }
            else: 
                if not final_llm_answer_content:
                    fallback_message = "I'm not sure how to respond to that or an issue occurred."
                    st.markdown(fallback_message)
                    assistant_message_to_store = {"role": "assistant", "content": fallback_message}
            
            if assistant_message_to_store:
                if not st.session_state.messages or \
                   st.session_state.messages[-1].get("role") == "user" or \
                   st.session_state.messages[-1].get("content") != assistant_message_to_store.get("content") or \
                   st.session_state.messages[-1].get("tool_calls") != assistant_message_to_store.get("tool_calls") :
                    st.session_state.messages.append(assistant_message_to_store)
