# Neo Chatbot

This repository contains the **Neo Chatbot** agent built using the [Microsoft Agent Framework]. It supports an interactive CLI mode and a complete, visually appealing **Streamlit User Interface**.

Neo can act as a general helpful chatbot, intelligently remembering conversation history and maintaining context. It also has specialized arithmetic tools (addition, subtraction, multiplication, and division) which it correctly identifies and utilizes when given math-related queries.

## 🚀 Features
- **Conversational Memory:** Neo keeps track of context both within the interface using Streamlit session state, and natively via the framework's internal memory provider.
- **Agentic Tools:** Neo natively executes bound python functions (add, subtract, etc.) when needed to correctly compute responses before replying.
- **Multi-Agent Orchestration:** Demonstrate concurrent workflow capabilities using `ConcurrentBuilder` to coordinate Researcher, Marketer, and Legal agents on a single business prompt.
- **Streamlit Web UI:** A beautiful frontend chat interface to talk directly with Neo.
- **CLI Chatbot:** An interactive command-line interface `main.py` if you prefer working within the terminal.

## 📁 Repository Structure
```
.
├── assets/                  # Contains custom images and logos
│   ├── logo.png             # UI Header Logo 
│   └── neo.png              # Assistant Chat Avatar
├── core/                    # Core bot logic and Microsoft Agent Framework configurations
│   ├── __init__.py
│   ├── agent.py             # Agent definitions, context providers, and prompt instructions
│   ├── memory.py            # FileSessionStorage and user-memory state persistence
│   └── tools.py             # Bound math functions executable by the agent
├── orchestration_concurrent/# Advanced multi-agent orchestration examples
│   ├── config.py            # Shared configuration for orchestrations
│   └── multi_agent.py       # Concurrent workflow execution script
├── .env.example             # Template for required environment configuration
├── main.py                  # CLI interactive execution point
├── requirements.txt         # Project package dependencies
└── streamlit_app.py         # Streamlit UI execution point
```

## 🛠️ Setup & Installation

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Install Packages
It is heavily recommended to use a virtual environment.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the `.env.example` file to a new `.env` file and populate it with your specific Azure OpenAI details.

```bash
cp .env.example .env
```

You will need:
- `AZURE_OPENAI_ENDPOINT`: Your endpoint URL
- `AZURE_OPENAI_API_KEY`: Your key
- `DEPLOYMENT_NAME`: The specific model deployment name 
- `OPENAI_API_VERSION`: Optional (defaults natively to 2025-03-01-preview)

## 💻 Usage

### Running the Streamlit UI (Recommended)
You can launch the web interface locally using:
```bash
streamlit run streamlit_app.py
```
This will open your default web browser to the Chat UI with the custom Neo bot avatar and logo.

### Running the CLI Interactive Mode
To run the interactive loop directly in your terminal:
```bash
python main.py
```

To run a single prompt query directly from the terminal without entering conversational mode:
```bash
python main.py "Please add 10 and 42"
```

### Advanced: Multi-Agent Orchestration
This repository also contains an implementation of **Concurrent Multi-Agent Orchestration** utilizing the framework's `ConcurrentBuilder`.

Located in `orchestration_concurrent/multi_agent.py`, this script spins up three distinct personas simultaneously:
1. **Researcher**: Provides factual insights and market opportunities.
2. **Marketer**: Crafts compelling value propositions.
3. **Legal**: Highlights compliance constraints and disclaimers.

A single user prompt is broadcast to all three agents in parallel. The orchestrator waits for all agents to finish processing, then aggregates their individual expert responses into a single combined output stream.

To execute the multi-agent concurrency test, run:
```bash
python -m orchestration_concurrent.multi_agent
```

## ⚠️ Notes
- The chatbot stores its temporary memory to a local json file (`.neo_session.json` by default). The CLI will intentionally clear this out prior to every run to establish a fresh session. The Streamlit UI maintains history per active session inside `st.session_state`.
