"""
Simple agent that uses a model to generate responses.
Supports tool calling via OpenAI-compatible API.
"""

import json

from src.agents.openai_client import create_openai_client
from src.agents.topic_relevancy import classify_query
from src.message_templates import REFUSAL_TEMPLATES


class SimpleAgent:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "openrouter:nvidia/nemotron-3-nano-30b-a3b:free",
        system_prompt: str | None = None,
        max_iterations: int = 10,
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

        query_classification = classify_query(
            query, self.context[1:]
        )  # Exclude system prompt from context for classification
        print(query_classification, query_classification.get("allowed", True))
        if not query_classification.get("allowed", True):
            reason = query_classification.get("reason", "unknown reason")
            print(f"Query classified as not allowed: {reason}")
            if len(self.context) > 2:
                refusal = REFUSAL_TEMPLATES["topic_drift"]
            else:
                refusal = REFUSAL_TEMPLATES["off_topic"]
            self.context.append({"role": "assistant", "content": refusal})
            return refusal

        output = ""
        turns = 0
        max_retry = 2

        while turns < self.max_iterations:
            api_kwargs = {"messages": self.context, "model": self.model}
            if self.tools:
                api_kwargs["tools"] = self.tools

            retry_count = 0
            while retry_count < max_retry:
                result = self.client.chat.completions.create(**api_kwargs)
                finish_reason = result.choices[0].finish_reason
                message = result.choices[0].message
                if finish_reason == "stop" and message.content is None and not message.tool_calls:
                    print(
                        f"Warning: model returned empty response, retrying ({retry_count + 1}/{max_retry})..."
                    )
                    retry_count += 1
                    continue
                break

            if retry_count >= max_retry:
                output = (
                    "I'm sorry, I wasn't able to generate a response. Could you try rephrasing?"
                )
                self.context.append({"role": "assistant", "content": output})
                break

            if finish_reason == "stop":
                output = message.content
                self.context.append({"role": "assistant", "content": output})
                break

            elif finish_reason == "length":
                # TODO: Handle by retrying
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

                    if not isinstance(tool_result, str):
                        tool_result = json.dumps(tool_result)

                    self.context.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result,
                        }
                    )

            turns += 1

        return output

    def reset(self):
        self.context = []
        self.client = create_openai_client(api_key=self._api_key, base_url=self._base_url)
        if self.system_prompt:
            self.context.append({"role": "system", "content": self.system_prompt})

    def get_context(self) -> list[dict[str, str]]:
        return self.context
