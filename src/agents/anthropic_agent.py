"""
Anthropic agent that uses the Messages API for book recommendations.
Supports tool calling with the same tool schemas as SimpleAgent (auto-converted from OpenAI format).
"""

import json

from src.agents.anthropic_client import create_anthropic_client


def _convert_openai_tools_to_anthropic(tools: list[dict]) -> list[dict]:
    """Convert OpenAI-format tool schemas to Anthropic format.

    OpenAI:    {"type": "function", "function": {"name": X, "description": Y, "parameters": Z}}
    Anthropic: {"name": X, "description": Y, "input_schema": Z}
    """
    anthropic_tools = []
    for tool in tools:
        func = tool["function"]
        anthropic_tools.append(
            {
                "name": func["name"],
                "description": func["description"],
                "input_schema": func["parameters"],
            }
        )
    return anthropic_tools


class AnthropicAgent:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-20250514",
        system_prompt: str | None = None,
        max_iterations: int = 10,
        tools: list[dict] | None = None,
        tool_handlers: dict | None = None,
    ):
        """
        Anthropic agent with optional tool calling.

        Args:
            tools: OpenAI-format tool schemas (auto-converted to Anthropic format).
            tool_handlers: Dict mapping tool name to callable.
        """
        self.context = []
        self.client = create_anthropic_client(api_key=api_key)
        self._api_key = api_key
        self.model = model
        self.system_prompt = system_prompt or ""
        self.max_iterations = max_iterations
        self.tools = tools
        self.anthropic_tools = (
            _convert_openai_tools_to_anthropic(tools) if tools else []
        )
        self.tool_handlers = tool_handlers or {}

    def run(self, query: str) -> str:
        """Run the agent loop. Returns the final assistant text response."""
        self.context.append({"role": "user", "content": query})
        output = ""
        turns = 0
        max_retry = 2

        while turns < self.max_iterations:
            api_kwargs = {
                "model": self.model,
                "system": self.system_prompt,
                "messages": self.context,
                "max_tokens": 4096,
            }
            if self.anthropic_tools:
                api_kwargs["tools"] = self.anthropic_tools

            retry_count = 0
            while retry_count < max_retry:
                result = self.client.messages.create(**api_kwargs)
                # Check for empty response (no content blocks or all empty)
                text_blocks = [b for b in result.content if b.type == "text"]
                tool_blocks = [b for b in result.content if b.type == "tool_use"]
                if (
                    result.stop_reason == "end_turn"
                    and not text_blocks
                    and not tool_blocks
                ):
                    print(
                        f"Warning: model returned empty response, retrying ({retry_count + 1}/{max_retry})..."
                    )
                    retry_count += 1
                    continue
                break

            if retry_count >= max_retry:
                output = "I'm sorry, I wasn't able to generate a response. Could you try rephrasing?"
                self.context.append({"role": "assistant", "content": output})
                break

            if result.stop_reason in ("end_turn", "max_tokens"):
                if result.stop_reason == "max_tokens":
                    print("Warning: response truncated due to max token limit.")

                # Append the full assistant message to context
                self.context.append({"role": "assistant", "content": result.content})

                # Extract text from content blocks
                output = "\n".join(b.text for b in text_blocks)
                break

            elif result.stop_reason == "tool_use":
                # Append the full assistant message (may contain text + tool_use blocks)
                self.context.append({"role": "assistant", "content": result.content})

                # Process each tool call and collect results
                tool_results = []
                for block in tool_blocks:
                    name = block.name
                    args = block.input

                    if name not in self.tool_handlers:
                        tool_result = json.dumps({"error": f"Unknown tool: {name}"})
                    else:
                        try:
                            tool_result = self.tool_handlers[name](**args)
                        except Exception as e:
                            tool_result = json.dumps(
                                {"error": f"{type(e).__name__}: {e}"}
                            )

                    if not isinstance(tool_result, str):
                        tool_result = json.dumps(tool_result)

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_result,
                        }
                    )

                # Anthropic expects tool results in a user message
                self.context.append({"role": "user", "content": tool_results})

            turns += 1

        return output

    def reset(self):
        self.context = []
        self.client = create_anthropic_client(api_key=self._api_key)

    def get_context(self) -> list[dict]:
        return self.context
