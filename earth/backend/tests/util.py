import json

from httpx import AsyncClient, Response


def is_subset(subset, superset):
    """
    Check if `subset` is a subset of `superset`. Works with nested dictionaries and lists.

    Args:
        subset: The subset to check.
        superset: The superset to check against.

    Returns:
        True if `subset` is a subset of `superset`, False otherwise.
    """
    match subset:
        case dict(_):
            return all(
                key in superset and is_subset(val, superset[key])
                for key, val in subset.items()
            )
        case list(_) | set(_):
            return all(
                any(is_subset(subitem, superitem) for superitem in superset)
                for subitem in subset
            )
        # assume that subset is a plain value if none of the above match
        case _:
            return subset == superset


async def check_request(
    async_client: AsyncClient,
    method: str,
    url: str,
    data: dict,
    expect: dict,
    error_message="",
):
    """
    Send a request using the provided `async_client` and check if the response matches the expected values.

    Args:
        async_client (AsyncClient): The async HTTP client to use for sending the request.
        method (str): The HTTP method to use for the request.
        url (str): The URL to send the request to.
        data (dict): The data (body) to send in the request.
        expect (dict): The expected values to check in the response.
        error_message (str): The error message to display if the response does not match the expected values.

    Returns:
        Response: The response object.

    Raises:
        AssertionError: If any of the expected values are not present in the response.
    """
    response: Response = await async_client.request(method=method, url=url, json=data)
    for attr, expect in expect.items():
        actual = getattr(response, attr)
        if callable(actual):
            actual = actual()
        message = (
            error_message
            + f" for attribute {attr}\n"
            + f"  Expected: {expect}\n"
            + f"  Got: {actual}\nActual response.json():\n"
            + json.dumps(response.json(), indent=2)
        )
        assert is_subset(expect, actual), message
    return response


def print_json(*objs):
    for obj in objs:
        print(json.dumps(obj, indent=2))
