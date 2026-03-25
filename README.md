# Eddie Chatbot - Microsoft Agent Framework

Eddie is a friendly and helpful conversational agent built using the **Microsoft Agent Framework**. It demonstrates how to integrate Azure OpenAI with custom tools and memory providers to create an interactive AI experience.

## ✨ Key Features

- **Conversational Intelligence**: Powered by Azure OpenAI's Responses API for natural and engaging interactions.
- **Arithmetic Tools**: Eddie can perform mathematical operations using built-in tools for:
  - Addition (`add`)
  - Subtraction (`subtract`)
  - Multiplication (`multiply`)
  - Division (`divide`)
- **Contextual Memory**:
  - **Conversation History**: Eddie remembers the flow of the current conversation.
  - **User Personalization**: Includes a custom `UserMemoryProvider` that can learn and remember your name (e.g., just say "My name is Alice").
- **Flexible CLI Interface**:
  - **Interactive Mode**: A continuous chat loop for ongoing conversations.
  - **Single Query Mode**: Execute a specific command and exit immediately.
- **Session Persistence**: Built-in support for saving session state to a local JSON file (`.eddie_session.json`).

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- An active **Azure OpenAI Service** subscription.

### 1. Setup Environment

Create a `.env` file in the root directory and add your Azure OpenAI configuration:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
DEPLOYMENT_NAME=your-deployment-name
OPENAI_API_VERSION=2025-03-01-preview
```

### 2. Install Dependencies

Install the required packages using `pip`:

```bash
pip install -r requirements.txt
```

*Note: For orchestration features, you may need to install with the `--pre` flag as indicated in `requirements.txt`.*

### 3. Run the Chatbot

#### Interactive Mode
Start a continuous conversation with Eddie:
```bash
python main.py
```

#### Single Query Mode
Ask a specific question directly from the terminal:
```bash
python main.py "What is 125 divided by 5?"
```

## 📂 Project Structure

- `main.py`: The entry point for the CLI application.
- `agent.py`: Agent definition, instructions, and tool registration using Microsoft Agent Framework.
- `tools.py`: Implementation of the arithmetic tools with framework-specific logging.
- `memory.py`: Custom memory providers and session storage logic.
- `requirements.txt`: Project dependencies and installation notes.

## 📝 Commands

In interactive mode, you can use the following commands to exit:
- `quit`
- `exit`
- `q`
