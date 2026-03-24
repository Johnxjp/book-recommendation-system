import logfire
from openai import OpenAI

logfire.configure()


def create_openai_client(
    api_key: str = None,
    base_url: str = None,
    timeout: float = 10,
) -> OpenAI:
    """
    Creates a chat completion client using OpenAI SDK.
    This supports OpenRouter models or OpenAI models depending on the base_url provided.
    """
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
    logfire.instrument_openai(client)
    return client

