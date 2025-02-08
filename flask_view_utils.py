from flask import redirect, request, url_for


def full_url_for(*args, **kwargs):
    # get the current domain and port, e.g. if we're running locally
    endpoint = url_for(*args, **kwargs)
    url = request.host_url + endpoint
    print(f"url = {url}")
    return url


def redirect_to_view(blueprint, view_func, **kwargs):
    # e.g. redirect_to_view(views_bp, languages)
    return redirect(url_for(blueprint.name + "." + view_func.__name__, **kwargs))
