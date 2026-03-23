"""
Simple agent that uses a model to generate responses.
Supports tool calling via OpenAI-compatible API.
"""

import json

from src.agents.openai_client import create_openai_client


class SimpleAgent:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "openrouter:nvidia/nemotron-3-nano-30b-a3b:free",
        system_prompt: str | None = None,
        max_iterations: int = 5,
        tools: list[dict] | None = None,
        tool_handlers: dict | None = None,
    ):
        """
        Simple agent with optional tool calling.

        Args:
            tools: OpenAI-format tool schemas sent to the API.
            tool_handlers: Dict mapping tool name to callable.
        """
        self.context = []
        self.client = create_openai_client(api_key=api_key, base_url=base_url)
        self._api_key = api_key
        self._base_url = base_url
        self.model = model
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.tools = tools
        self.tool_handlers = tool_handlers or {}
        if self.system_prompt:
            self.context.append({"role": "system", "content": self.system_prompt})

    def run(self, query: str) -> str:
        """Run the agent loop. Returns the final assistant text response."""
        self.context.append({"role": "user", "content": query})
        output = ""
        turns = 0

        while turns < self.max_iterations:
            api_kwargs = {"messages": self.context, "model": self.model}
            if self.tools:
                api_kwargs["tools"] = self.tools

            result = self.client.chat.completions.create(**api_kwargs)
            finish_reason = result.choices[0].finish_reason
            message = result.choices[0].message

            if finish_reason == "stop":
                output = message.content
                self.context.append({"role": "assistant", "content": output})
                break

            elif finish_reason == "length":
                output = message.content
                self.context.append({"role": "assistant", "content": output})
                print("Warning: response truncated due to max token limit.")
                break

            elif finish_reason == "tool_calls":
                # Append the assistant message with tool calls to context
                self.context.append(message)

                for tool_call in message.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    if name not in self.tool_handlers:
                        tool_result = json.dumps({"error": f"Unknown tool: {name}"})
                    else:
                        try:
                            tool_result = self.tool_handlers[name](**args)
                        except Exception as e:
                            tool_result = json.dumps({"error": f"{type(e).__name__}: {e}"})

                    self.context.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    })

            turns += 1

        return output

    def reset(self):
        self.context = []
        self.client = create_openai_client(api_key=self._api_key, base_url=self._base_url)
        if self.system_prompt:
            self.context.append({"role": "system", "content": self.system_prompt})

    def get_context(self) -> list[dict[str, str]]:
        return self.context
