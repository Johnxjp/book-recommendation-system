import logfire
from anthropic import Anthropic

logfire.configure()


def create_anthropic_client(
    api_key: str | None = None,
    timeout: float = 30,
) -> Anthropic:
    """
    Creates an Anthropic client for the Messages API.
    """
    client = Anthropic(api_key=api_key, timeout=timeout)
    logfire.instrument_anthropic(client)
    return client
