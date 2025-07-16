from typing import TypeVar

from scrapeless import Scrapeless

T = TypeVar("T", Scrapeless, Scrapeless)


def create_scrapeless_client(client_cls: type[T], token: str) -> T:
    """Create a Scrapeless client instance with the provided API token.

    Args:
        client_cls (type[T]): The Scrapeless client class to instantiate.
        token (str): API token for Scrapeless.
    Returns:
        T: An instance of the Scrapeless client class.
    Raises:
        ValueError: If the API token is not provided.
    """
    if not token:
        msg = "API token is required to create a Scrapeless client."
        raise ValueError(msg)

    client = client_cls(
        {
            "api_key": token,
        }
    )

    return client
