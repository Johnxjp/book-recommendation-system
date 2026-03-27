import logfire
from openai import AsyncOpenAI, OpenAI

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


def create_async_openai_client(
    api_key: str = None,
    base_url: str = None,
    timeout: float = 30,
) -> AsyncOpenAI:
    """
    Creates an async chat completion client using OpenAI SDK.
    Used by the streaming agent for non-blocking SSE responses.
    """
    client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
    logfire.instrument_openai(client)
    return client
