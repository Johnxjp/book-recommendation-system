import json
import uuid
from datetime import datetime
from pathlib import Path

from src.agents.simple import SimpleAgent
from src.prompts.base import prompt

MODEL = "openrouter:nvidia/nemotron-3-nano-30b-a3b:free"
LOGS_DIR = Path("logs")


def save_log(log: dict):
    LOGS_DIR.mkdir(exist_ok=True)
    filepath = LOGS_DIR / f"{log['session_id']}.json"
    with open(filepath, "w") as f:
        json.dump(log, f, indent=4)
    print(f"Session log saved to {filepath}")


def main():
    agent = SimpleAgent(model=MODEL, system_prompt=prompt)

    log = {
        "session_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "system_prompt": prompt,
        "tools": [],
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

            response = agent.get_response(user_input)

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
