\# Nexus AI



Nexus AI is a local-first AI assistant project exploring Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), Model Context Protocol (MCP), and safe AI tool execution.



\## Features



\- Local LLM integration using Ollama.

\- Agent workflows and tool selection.

\- MCP server and agent experiments.

\- Allowlisted tool execution.

\- Order lookup with input validation.

\- Safety-focused tests for invalid tools and arguments.



\## Tech Stack



\- Python

\- Ollama

\- MCP

\- Pytest



\## Project Structure



```text

nexus-ai/

&#x20; app/

&#x20;   llm/

&#x20;     local\_llm.py

&#x20; data/

&#x20; agent.py

&#x20; mcp\_agent.py

&#x20; mcp\_server.py

&#x20; order\_tools.py

&#x20; tool\_executor.py

&#x20; test\_unapproved\_tool.py

&#x20; .gitignore

&#x20; README.md

\## Getting Started



\### 1. Create and activate a virtual environment



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



\### 2. Install dependencies



Install the required Python packages in your virtual environment. The Ollama Python client is available through:



```powershell

python -m pip install ollama

```



Ensure Ollama is installed and running locally, and that your configured model is available before running LLM workflows.



\### 3. Run the tests



```powershell

python -m pytest -v

```



\## Safety



Nexus AI experiments with allowlisted tools and strict argument validation. Tool execution should remain limited to explicitly approved operations.



\## Project Status



Under active development. Features and documentation will evolve as the project grows.
