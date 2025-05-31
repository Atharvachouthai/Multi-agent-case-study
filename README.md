# Multi-Tool LLM Agent with Groq & LangGraph

## Objective
This project implements an LLM-powered autonomous agent designed to:
* Interpret complex natural language tasks.
* Choose appropriate tools (web search, calculator, Python code execution, document summarization).
* Break tasks into subgoals (handled implicitly by the LLM).
* Execute or delegate subtasks to its tools.
* Maintain short-term memory for conversational context.

This project fulfills core requirements of the AI Engineer Assignment, demonstrating the design and implementation of a functional multi-tool agent with a Streamlit UI.

## Features
* **Natural Language Understanding:** Leverages LLaMA 3 8B via the Groq API for understanding user queries.
* **Tool Integration:** Equipped with four distinct tools:
    * `web_search`: Fetches information from the internet using DuckDuckGo.
    * `calculator`: Evaluates mathematical expressions.
    * `python_code_executor`: Executes simple Python code snippets.
    * `document_summarizer`: Summarizes provided text using an LLM.
* **Autonomous Tool Selection:** The agent decides which tool to use based on the query.
* **Conversational Interface:** A Streamlit web application provides an interactive chat interface.
* **Modular Design:** Code is organized into logical modules for configuration, tools, agent graph logic, and the UI.
* **Short-Term Memory:** Maintains conversation history within a session to provide context for ongoing interactions.
* **Prompt Engineering:** Utilizes a system prompt and descriptive tool docstrings to guide the LLM's behavior and tool usage.

## Tech Stack
* **LLM Backend:** LLaMA 3 8B via [Groq API](https://groq.com/) (for fast inference).
* **Orchestration:** [LangGraph](https://python.langchain.com/docs/langgraph) (for building the agent's stateful, cyclical reasoning process).
* **Core LLM Framework:** [LangChain](https://python.langchain.com/) (for message types, tool definitions, LLM integrations).
* **Tools:** Custom Python functions.
* **Web Search:** `duckduckgo-search` library.
* **UI:** [Streamlit](https://streamlit.io/).
* **Programming Language:** Python 3.9+

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
    cd YOUR_REPOSITORY_NAME
    ```
    *(Replace `YOUR_USERNAME/YOUR_REPOSITORY_NAME` with your actual GitHub details after you create the repo).*

2.  **Create and Activate a Python Virtual Environment:**
    It's highly recommended to use a virtual environment.
    ```bash
    python3 -m venv my_venv 
    source my_venv/bin/activate  # On Windows: my_venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    Ensure you have the `requirements.txt` file in your project root.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Key:**
    This agent uses the Groq API. You need to obtain an API key from [GroqCloud](https://console.groq.com/).
    Set your Groq API key as an environment variable. In your terminal session:
    * **macOS/Linux:**
        ```bash
        export GROQ_API_KEY='your_gsk_actual_key_here'
        ```
    * **Windows (PowerShell):**
        ```powershell
        $env:GROQ_API_KEY='your_gsk_actual_key_here'
        ```
    Replace `'your_gsk_actual_key_here'` with your actual key. For the application to find it every time, you might want to add this line to your shell's startup file (e.g., `~/.zshrc`, `~/.bash_profile`).

## How to Run
1.  Ensure your virtual environment is activated and the `GROQ_API_KEY` is set.
2.  Navigate to the project's root directory in your terminal.
3.  Run the Streamlit application:
    ```bash
    streamlit run streamlit_app.py
    ```
    This will open the application in your web browser.

## File Structure Overview
* `streamlit_app.py`: Main file for the Streamlit web interface. Handles user interaction and calls the agent.
* `agent_graph.py`: Defines the LangGraph agent, its state, nodes (LLM, tools), and edges (control flow). Contains the core agent logic and system prompt.
* `tools_definition.py`: Contains the Python functions for each tool available to the agent (web_search, calculator, etc.) and their `@tool` decorators with descriptive docstrings.
* `config.py`: Manages configuration variables like API keys and LLM model names.
* `requirements.txt`: Lists the Python dependencies for the project.
* `.gitignore`: Specifies intentionally untracked files that Git should ignore.
* `README.md`: This file.

## Acknowledgements and Resources Used
This project was developed with the assistance and learning gained from the following resources:
* **Gemini (by Google):** For AI-powered assistance in understanding concepts, debugging, and refining project ideas.
* **NotebookLM (by Google):** For further research and understanding various concepts related to LLMs, agent architecture, and Python libraries.
* **LangGraph Documentation:** [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/?_gl=1*1tc2nj1*_ga*ODk2NzEwMjg4LjE3NDg2OTU0Mzc.*_ga_47WX3HKKY2*czE3NDg3MTIwNDIkbzIkZzAkdDE3NDg3MTIwNDIkajYwJGwwJGgw)
* Various other articles and documentation related to LangChain, Streamlit, and general Python development.

## Project Status & Future Work

This project successfully implements a multi-tool LLM agent with a user-friendly Streamlit interface, covering core aspects of the assignment such as agent design, tool integration with four distinct tools (web search, calculator, Python code executor, document summarizer), prompt engineering, and short-term memory management.

Due to the complexity and time constraints inherent in developing advanced AI agent features, the following assignment tasks were not fully implemented:

* **Assignment Task 4 - Long-Term Memory:** While short-term memory is functional, persistent long-term memory (task history, persistent knowledge across sessions) has not been integrated.
* **Assignment Task 5 - Full Evaluation Suite Execution & Analysis:** Benchmark queries and evaluation metrics have been designed. However, the comprehensive execution of these benchmarks and a detailed written analysis of the agent's performance against all metrics is a pending step. The agent has been tested with various complex queries during development, demonstrating its core functionalities.
* **Assignment Task 6 (Bonus) - Autonomous Looping & Error Handling:** Advanced features like automatic tool retries or dynamic plan revision based on subgoal failures were not implemented. The agent currently relies on the LLM's inherent resilience and basic error catching within tools.

This project has been an incredible learning experience, allowing exploration and application of concepts in LLM orchestration, tool use, prompt engineering, and agentic design. Regardless of the outcome of this assignment, I am keen to continue refining this agent, implementing the remaining features, and further exploring the potential of multi-tool LLM systems.