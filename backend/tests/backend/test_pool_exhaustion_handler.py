"""Pool exhaustion must surface as 503, not 500 (and never 400).

Under crawler load the 14-slot pool can be fully in use, and a request that never
gets a slot is transient overload rather than a crash. Serving it as 500 hid a
capacity problem inside the generic error handler and gave clients no reason to
back off.

The 400 case is the subtle one: `playhouse.pool.MaxConnectionsExceeded` subclasses
`ValueError`, so handlers that map bad input to 400 were reporting overload as
malformed input. `db_connection` therefore translates it to
`DatabaseOverloadedError`, which these tests pin down.
"""

import pytest
from flask import Flask
from playhouse.pool import MaxConnectionsExceeded

from utils.db_connection import MonitoredPooledPostgresqlExtDatabase
from utils.exceptions import DatabaseOverloadedError
from utils.error_utils import (
    register_pool_exhaustion_handler,
    POOL_EXHAUSTION_RETRY_AFTER,
)


@pytest.fixture
def app():
    app = Flask(__name__)
    # Let genuine exceptions propagate so we can assert the handler is selective
    # rather than relying on Flask's default "anything unhandled becomes 500".
    app.config["PROPAGATE_EXCEPTIONS"] = True
    register_pool_exhaustion_handler(app)

    @app.route("/api/lang/overloaded")
    def api_overloaded():
        raise DatabaseOverloadedError("Max connections exceeded, timed out.")

    @app.route("/api/lang/raw")
    def api_raw():
        # Belt and braces: any path still raising the playhouse type directly.
        raise MaxConnectionsExceeded("Exceeded maximum connections.")

    @app.route("/web/overloaded")
    def web_overloaded():
        raise DatabaseOverloadedError("Max connections exceeded, timed out.")

    @app.route("/api/lang/bug")
    def api_bug():
        raise ValueError("a genuine bug")

    return app


@pytest.mark.parametrize("path", ["/api/lang/overloaded", "/api/lang/raw"])
def test_api_route_returns_503_json(app, path):
    response = app.test_client().get(path)
    assert response.status_code == 503
    assert response.headers["Retry-After"] == str(POOL_EXHAUSTION_RETRY_AFTER)
    assert response.get_json()["status_code"] == 503


def test_web_route_returns_503(app):
    response = app.test_client().get("/web/overloaded")
    assert response.status_code == 503
    assert response.headers["Retry-After"] == str(POOL_EXHAUSTION_RETRY_AFTER)


def test_handler_is_selective(app):
    """A genuine ValueError must pass straight through, untouched.

    Asserting on the propagated exception rather than a 500 status matters: with
    Flask's default behaviour a catch-all handler returning 500 would also produce
    a 500 here, so status alone proves nothing about selectivity.
    """
    with pytest.raises(ValueError) as excinfo:
        app.test_client().get("/api/lang/bug")
    assert not isinstance(excinfo.value, DatabaseOverloadedError)


def test_overload_error_is_not_a_value_error():
    """The whole point of the custom type: `except ValueError -> 400` must miss it."""
    assert not issubclass(DatabaseOverloadedError, ValueError)
    assert issubclass(MaxConnectionsExceeded, ValueError)


def test_connect_translates_pool_exhaustion():
    """The translation itself, at the boundary where it actually happens.

    The tests above raise the already-translated type by hand, so they would stay
    green if `MonitoredPooledPostgresqlExtDatabase.connect()` went back to a plain
    `raise`. This one drives the real `connect()` with an exhausted pool, so the
    contract is pinned where it is implemented.

    No server is touched: `_connect` is replaced, so no socket is ever opened.
    """
    db = MonitoredPooledPostgresqlExtDatabase(
        "unused-in-this-test",
        max_connections=1,
        stale_timeout=600,
        timeout=1,
        autoconnect=True,
        thread_safe=True,
    )
    # Keep the retry loop short; playhouse sleeps 0.1s between attempts.
    db._wait_timeout = 0.01

    def always_exhausted(*args, **kwargs):
        raise MaxConnectionsExceeded("Exceeded maximum connections.")

    db._connect = always_exhausted

    with pytest.raises(DatabaseOverloadedError) as excinfo:
        db.connect()

    # The original stays attached, so tracebacks still name the real cause.
    assert isinstance(excinfo.value.__cause__, MaxConnectionsExceeded)
