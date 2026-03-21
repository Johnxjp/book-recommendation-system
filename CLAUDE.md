# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Book recommendation systems — an early-stage Python project exploring AI agents for book recommendations.

## References
Project plans is contained in /scratchpad

- `scratchpad/spec.md`: project specification

## Commands

- **Run an agent:** `uv run python src/agents/base.py`
- **Add a dependency:** `uv add <package>`
- **Sync dependencies:** `uv sync`

## Dependencies

Dependencies are managed with `uv`. 
Always check `pyproject.toml` for existing packages before attempting to install new ones.

## Architecture

- **Python 3.12**, managed with **uv** (see `uv.lock`)
- Agent framework: **Pydantic AI** (`pydantic-ai-slim[openrouter]`) — use `OpenRouterModel` + `OpenRouterProvider` for model setup
- All LLM calls route through **OpenRouter** using `OPENROUTER_API_KEY` from `.env`
- Agent definitions live in `src/agents/`
- Environment variables loaded via `python-dotenv`; see `.env.example` for required keys
