from datetime import datetime
import json
import os
from pathlib import Path
import uuid

from dotenv import load_dotenv

from src.agents.simple import SimpleAgent
from src.db import get_connection
from src.prompts.base import prompt
from src.tools.user_reading_history import user_history_tools, make_handlers
from src.utils import fetch_openrouter_models

load_dotenv()

LOGS_DIR = Path("logs")


def save_log(log: dict):
    LOGS_DIR.mkdir(exist_ok=True)
    filepath = LOGS_DIR / f"{log['session_id']}.json"
    with open(filepath, "w") as f:
        json.dump(log, f, indent=4)
    print(f"Session log saved to {filepath}")


def main():
    try:
        model = os.getenv("AGENT_MODEL") or "nvidia/nemotron-3-nano-30b-a3b:free"
        base_url = os.getenv("BASE_URL") or None
        api_key = os.getenv("OPENROUTER_API_KEY") or None

        print(f"Using base URL: {base_url}")
        print(f"Using model: {model}")
        if "openrouter" in base_url:
            try:
                available_models = fetch_openrouter_models(api_key=api_key, base_url=base_url)
                if model not in available_models:
                    print(f"Model '{model}' not found in OpenRouter. Available models:")
                    return
            except Exception as e:
                print(f"Error fetching OpenRouter models: {e}")
                raise

        conn = get_connection("data/books.db")
        tool_handlers = make_handlers(conn)

        agent = SimpleAgent(
            api_key=api_key,
            base_url=base_url,
            model=model,
            system_prompt=prompt,
            max_iterations=5,
            tools=user_history_tools,
            tool_handlers=tool_handlers,
        )
        print("Agent initialized successfully with the following configuration:")
        print(f"Model: {model}")
        print(f"System Prompt: {prompt}")
        print(f"Tools: {[t['function']['name'] for t in user_history_tools]}")

    except Exception as e:
        print(f"Error initializing agent: {e}")
        return

    log = {
        "session_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "system_prompt": prompt,
        "tools": [t["function"]["name"] for t in user_history_tools],
        "conversation": [],
    }
    turn = 0

    print("Book Recommendation Agent")
    print("Type 'quit' to exit.\n")

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
