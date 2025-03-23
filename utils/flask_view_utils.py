from flask import redirect, request, url_for
from utils.url_registry import endpoint_for


def full_url_for(*args, **kwargs):
    # get the current domain and port, e.g. if we're running locally
    endpoint = url_for(*args, **kwargs)
    url = request.host_url + endpoint
    print(f"url = {url}")
    return url
