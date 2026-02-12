---
name: pydantic-ai
description: Use when the user asks about Pydantic AI, a Python agent framework designed to help you quickly, confidently, and painlessly build production grade applications and workflows with Generative AI. Pydantic AI brings the FastAPI feeling to GenAI app and agent development by leveraging Pydantic Validation and modern Python features like type hints.
---


# Pydantic AI
Pydantic AI is a Python agent framework designed to help you quickly, confidently, and painlessly build production grade applications and workflows with Generative AI.

## OpenRouter
Install support with
```
uv add "pydantic-ai-slim[openrouter]"
```
To use requires OPENROUTER_API_KEY to be set in the environment.
```
from pydantic_ai import Agent

agent = Agent('openrouter:anthropic/claude-sonnet-4-5')
...
```

Or initialise the model and provider directly:
```
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

model = OpenRouterModel(
    'anthropic/claude-sonnet-4-5',
    provider=OpenRouterProvider(api_key='your-openrouter-api-key'),
)
agent = Agent(model)
...
```


## Additional References

-  **[references/agents.md](references/agents.md)**: Guidelines on using Pydantic AI agents SDKs