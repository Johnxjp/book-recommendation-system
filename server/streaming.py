"""
StreamingAgent — async streaming wrapper around the SimpleAgent logic.

Yields SSE events as an async generator:
- text: streaming text tokens
- tool_call: tool execution status
- recommendation: structured book data after response completes
- error: error messages
- done: signals completion
"""

import asyncio
import json
import os

from dotenv import load_dotenv

from src.agents.openai_client import create_async_openai_client
from src.agents.topic_relevancy import classify_query
from src.message_templates import REFUSAL_TEMPLATES

load_dotenv()


class StreamingAgent:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        system_prompt: str | None = None,
        max_iterations: int = 10,
        tools: list[dict] | None = None,
        tool_handlers: dict | None = None,
    ):
        self.context: list[dict] = []
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self._base_url = base_url or os.getenv("BASE_URL")
        self.model = model or os.getenv(
            "AGENT_MODEL", "openrouter:nvidia/nemotron-3-nano-30b-a3b:free"
        )
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.tools = tools
        self.tool_handlers = tool_handlers or {}
        self.client = create_async_openai_client(
            api_key=self._api_key, base_url=self._base_url
        )
        if self.system_prompt:
            self.context.append({"role": "system", "content": self.system_prompt})

    async def run_stream(self, query: str):
        """Async generator that yields SSE event dicts."""
        self.context.append({"role": "user", "content": query})

        # Run guardrail classification (sync, so use to_thread)
        classification = await asyncio.to_thread(
            classify_query, query, self.context[1:]
        )
        if not classification.get("allowed", True):
            if len(self.context) > 2:
                refusal = REFUSAL_TEMPLATES["topic_drift"]
            else:
                refusal = REFUSAL_TEMPLATES["off_topic"]
            self.context.append({"role": "assistant", "content": refusal})
            yield {"event": "text", "data": json.dumps({"content": refusal})}
            yield {"event": "done", "data": "{}"}
            return

        turns = 0
        full_response = ""

        while turns < self.max_iterations:
            api_kwargs = {
                "messages": self._serialize_context(),
                "model": self.model,
                "stream": True,
            }
            if self.tools:
                api_kwargs["tools"] = self.tools

            # Accumulate streamed response
            content_parts = []
            tool_calls_acc: dict[int, dict] = {}
            finish_reason = None

            stream = await self.client.chat.completions.create(**api_kwargs)
            async for chunk in stream:
                choice = chunk.choices[0] if chunk.choices else None
                if not choice:
                    continue

                delta = choice.delta
                finish_reason = choice.finish_reason

                # Stream text tokens
                if delta.content:
                    content_parts.append(delta.content)
                    yield {
                        "event": "text",
                        "data": json.dumps({"content": delta.content}),
                    }

                # Accumulate tool calls
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_acc:
                            tool_calls_acc[idx] = {
                                "id": tc.id,
                                "name": tc.function.name
                                if tc.function and tc.function.name
                                else "",
                                "args": "",
                            }
                        if tc.function and tc.function.arguments:
                            tool_calls_acc[idx]["args"] += tc.function.arguments
                        if tc.id and not tool_calls_acc[idx]["id"]:
                            tool_calls_acc[idx]["id"] = tc.id
                        if (
                            tc.function
                            and tc.function.name
                            and not tool_calls_acc[idx]["name"]
                        ):
                            tool_calls_acc[idx]["name"] = tc.function.name

            assembled_content = "".join(content_parts)

            if finish_reason == "stop":
                full_response = assembled_content
                self.context.append({"role": "assistant", "content": full_response})
                break

            elif finish_reason == "length":
                full_response = assembled_content
                self.context.append({"role": "assistant", "content": full_response})
                break

            elif finish_reason == "tool_calls" and tool_calls_acc:
                # Build the assistant message with tool calls
                tool_calls_list = []
                for idx in sorted(tool_calls_acc.keys()):
                    tc_data = tool_calls_acc[idx]
                    tool_calls_list.append(
                        {
                            "id": tc_data["id"],
                            "type": "function",
                            "function": {
                                "name": tc_data["name"],
                                "arguments": tc_data["args"],
                            },
                        }
                    )

                assistant_msg = {"role": "assistant", "tool_calls": tool_calls_list}
                if assembled_content:
                    assistant_msg["content"] = assembled_content
                self.context.append(assistant_msg)

                # Execute each tool
                for tc in tool_calls_list:
                    name = tc["function"]["name"]
                    yield {
                        "event": "tool_call",
                        "data": json.dumps({"name": name, "status": "calling"}),
                    }

                    try:
                        args = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        args = {}

                    if name not in self.tool_handlers:
                        tool_result = json.dumps({"error": f"Unknown tool: {name}"})
                    else:
                        try:
                            tool_result = await asyncio.to_thread(
                                self.tool_handlers[name], **args
                            )
                        except Exception as e:
                            tool_result = json.dumps(
                                {"error": f"{type(e).__name__}: {e}"}
                            )

                    if not isinstance(tool_result, str):
                        tool_result = json.dumps(tool_result, default=str)

                    self.context.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": tool_result,
                        }
                    )

                    yield {
                        "event": "tool_call",
                        "data": json.dumps({"name": name, "status": "complete"}),
                    }

            turns += 1

        # Extract structured recommendations from the response
        if full_response:
            recommendations = await self._extract_recommendations(full_response)
            if recommendations:
                yield {
                    "event": "recommendation",
                    "data": json.dumps(recommendations),
                }

        yield {"event": "done", "data": "{}"}

    async def _extract_recommendations(self, response_text: str) -> list[dict]:
        """Extract book recommendations from the assistant's response using an LLM call."""
        extraction_prompt = (
            "Extract any book recommendations from the following text. "
            "Return a JSON array of objects with 'title', 'authors' (list of strings), "
            "and 'reason' (why it was recommended, 1 sentence). "
            "If no books are recommended, return an empty array [].\n"
            "Return ONLY the JSON array, no other text.\n\n"
            f"Text:\n{response_text}"
        )
        try:
            result = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": extraction_prompt}],
                max_tokens=500,
            )
            raw = result.choices[0].message.content.strip()
            # Handle markdown code blocks
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                raw = raw.rsplit("```", 1)[0]
            books = json.loads(raw)
            if not isinstance(books, list):
                return []
            # Add cover URLs where possible
            for book in books:
                book["cover_url"] = None
            return books
        except Exception:
            return []

    def _serialize_context(self) -> list[dict]:
        """Serialize context for the API, handling non-serializable message objects."""
        serialized = []
        for msg in self.context:
            if isinstance(msg, dict):
                serialized.append(msg)
            else:
                # Handle OpenAI message objects stored in context
                d = {"role": msg.role}
                if msg.content:
                    d["content"] = msg.content
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    d["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ]
                serialized.append(d)
        return serialized

    def reset(self):
        self.context = []
        self.client = create_async_openai_client(
            api_key=self._api_key, base_url=self._base_url
        )
        if self.system_prompt:
            self.context.append({"role": "system", "content": self.system_prompt})
