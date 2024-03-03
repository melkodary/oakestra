import os

from requests import exceptions

RESOURCE_ABSTRACTOR_ADDR = (
    f"http://{os.environ.get('RESOURCE_ABSTRACTOR_URL')}:"
    f"{os.environ.get('RESOURCE_ABSTRACTOR_PORT')}"
)


def make_request(method, url, **kwargs):
    try:
        response = method(url, **kwargs)
        return response.json()
    except exceptions.RequestException:
        print(f"Calling {url} not successful.")

    return None