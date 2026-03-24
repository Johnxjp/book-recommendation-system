from datetime import datetime
import json
import os
from pathlib import Path
import uuid

from dotenv import load_dotenv

from src.agents.anthropic_agent import AnthropicAgent
from src.db import get_connection
from src.prompts.base import prompt
from src.tools.user_reading_history import user_history_tools_schema, make_handlers
from src.tools.web_tools import web_tools_schema, web_extract_tool, web_search_tool

load_dotenv()

LOGS_DIR = Path("logs")


def save_log(log: dict):
    LOGS_DIR.mkdir(exist_ok=True)
    filepath = LOGS_DIR / f"{log['session_id']}.json"
    with open(filepath, "w") as f:
        json.dump(log, f, indent=4, default=str)
    print(f"Session log saved to {filepath}")


def main():
    try:
        model = os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-20250514"
        api_key = os.getenv("ANTHROPIC_API_KEY") or None
        db_path = os.getenv("DB_PATH") or "data/books.db"

        if not api_key:
            print("Error: ANTHROPIC_API_KEY not set in environment.")
            return

        print(f"Using model: {model}")

        tools = user_history_tools_schema + web_tools_schema
        conn = get_connection(db_path)
        tool_handlers = make_handlers(conn)
        tool_handlers["web_search_tool"] = web_search_tool
        tool_handlers["web_extract_tool"] = web_extract_tool
        agent = AnthropicAgent(
            api_key=api_key,
            model=model,
            system_prompt=prompt,
            max_iterations=10,
            tools=tools,
            tool_handlers=tool_handlers,
        )
        print("Agent initialized successfully with the following configuration:")
        print(f"Model: {model}")
        print(f"Tools: {[t['function']['name'] for t in tools]}")

    except Exception as e:
        print(f"Error initializing agent: {e}")
        return

    log = {
        "session_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "system_prompt": prompt,
        "tools": [t["function"]["name"] for t in tools],
        "conversation": [],
    }

    # CLI
    print("Book Recommendation Agent (Anthropic)")
    print("Type 'quit' to exit.\n")

    turn = 0
    try:
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() == "quit":
                print("Goodbye!")
                break

            turn += 1
            log["conversation"].append(
                {
                    "turn": turn,
                    "role": "user",
                    "message": user_input,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            response = agent.run(user_input)

            turn += 1
            log["conversation"].append(
                {
                    "turn": turn,
                    "role": "assistant",
                    "message": response,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            print(f"\nAgent: {response}\n")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        save_log(log)


if __name__ == "__main__":
    main()
