import os

from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()


class BaseAgent:
    def __init__(self, model: str | None = None, system_prompt: str | None = None):
        self.model = model or os.getenv("OPENROUTER_DEFAULT_MODEL")
        self.agent = Agent(model=self.model, instructions=system_prompt)

    def get_response(self, query: str) -> str:
        result = self.agent.run_sync(query)
        return result.output


if __name__ == "__main__":
    agent = BaseAgent("openrouter:google/gemma-3-4b-it:free")
    response = agent.get_response("What is the capital of France?")
    print(response)
