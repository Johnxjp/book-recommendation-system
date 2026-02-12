"""
Single agent that uses a simple model to generate responses.
Does not have access to any tools.
"""

from src.agents.base import BaseAgent


class SimpleAgent(BaseAgent):
    def __init__(self, model: str | None = None, system_prompt: str | None = None):
        super().__init__(model=model, system_prompt=system_prompt)
        self.context = []

    def get_response(self, query: str) -> str:
        result = self.agent.run_sync(query, message_history=self.context)
        output = result.output
        self.context.append({"role": "user", "content": query})
        self.context.append({"role": "assistant", "content": output})
        return output

    def reset(self):
        self.context = []

    def get_context(self) -> list[dict[str, str]]:
        return self.context
