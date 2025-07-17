from typing import TypeVar

from scrapeless import Scrapeless

ScrapelessT = TypeVar("ScrapelessT", bound=Scrapeless)
AnyT = TypeVar("AnyT")


def create_scrapeless_client(client_cls: type[ScrapelessT], token: str) -> ScrapelessT:
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


def format_default_value(value: AnyT | None, default_value: AnyT) -> AnyT:
    """Format the default value of a Scrapeless client.

    Args:
        value (T | None): The value to format.
        default_value (T): The default value to return if value is None.

    Returns:
        T: The original value or the default value if original is None.
    """
    return default_value if value is None else value
