# llm-client

A minimal Python client that sends prompts to a local LLM (via Ollama),
handles errors gracefully, and saves every response to JSON.

This is the foundation of a larger project: an open-source security
testing tool for AI agents, focused on Spanish and Portuguese.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) with the `llama3.2` model

## Setup

    py -m venv .venv
    .venv\Scripts\activate
    pip install ollama
    ollama pull llama3.2

## Usage

    python main.py

Responses are saved to `resultados.json`.

## Roadmap

- [x] Local model client with error handling
- [ ] Attack test bank in Spanish
- [ ] Automated security report