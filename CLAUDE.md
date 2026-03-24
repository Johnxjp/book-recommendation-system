# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Book recommendation systems — an early-stage Python project exploring AI agents for book recommendations.

## References
Project plans is contained in /scratchpad

- `scratchpad/spec.md`: project specification

## Commands

- **Run OpenRouter agent:** `uv run python run_simple_agent.py`
- **Run Anthropic agent:** `uv run python run_anthropic_agent.py`
- **Add a dependency:** `uv add <package>`
- **Sync dependencies:** `uv sync`

## Dependencies

Dependencies are managed with `uv`. 
Always check `pyproject.toml` for existing packages before attempting to install new ones.

## Architecture

- **Python 3.12**, managed with **uv** (see `uv.lock`)
- Two LLM backends:
  - **OpenAI SDK** via OpenRouter (`OPENROUTER_API_KEY`, `BASE_URL`, `AGENT_MODEL`)
  - **Anthropic SDK** direct (`ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`)
- Agent definitions live in `src/agents/` — `SimpleAgent` (OpenAI) and `AnthropicAgent` (Anthropic)
- Tool schemas defined in OpenAI format in `src/tools/`; `AnthropicAgent` auto-converts at init
- Environment variables loaded via `python-dotenv`; see `.env.example` for required keys
