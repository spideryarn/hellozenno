"""Helpers for marking public, non-personalised GET responses as CDN-cacheable.

Vercel only serves a function response from its CDN when the response carries an
`s-maxage` directive - plain `max-age` is honoured by browsers but never avoids a
function invocation, which is where the cost is.

Two rules keep this safe:

1. We only set the header on requests with no `Authorization` header. Vercel
   already refuses to cache authenticated requests, but we need the same check
   ourselves because several read endpoints branch on auth *state*: anonymous
   callers get `authentication_required_for_generation` where logged-in callers
   trigger AI generation. Restricting ourselves to anonymous requests means a
   200 from those endpoints can only be the "row already existed" path.
2. Callers apply this on the success path only - never on a 401/404/error, and
   never on a response produced by generating missing content.

That first rule only protects logged-in users if their requests actually carry
the token. SvelteKit's server-side `fetch` does not attach it automatically, so
any `+page.server.ts` loader hitting a `cache_publicly` endpoint must forward
`locals.session.access_token` as a Bearer header - otherwise an editor's own SSR
request looks anonymous and can be served the shared cached copy of content they
just changed.
"""

from flask import Response, request

# Long enough to absorb repeat crawler hits on stable content, short enough that
# edits show up within the hour.
S_MAXAGE_DEFAULT = 3600
# Serve the stale copy for a day while the CDN refreshes in the background, so a
# cache miss after expiry still doesn't block on a function invocation.
STALE_WHILE_REVALIDATE_DEFAULT = 86400

# Content that effectively never changes (static language config, a specific
# immutable audio variant).
S_MAXAGE_LONG = 86400
STALE_WHILE_REVALIDATE_LONG = 604800

# Content a logged-in user can add to (e.g. new audio variants), where anonymous
# visitors shouldn't lag too far behind.
S_MAXAGE_SHORT = 300
STALE_WHILE_REVALIDATE_SHORT = 3600

# Pass this as stale_while_revalidate to cap how long a stale body can be served
# at s_maxage: stale-while-revalidate keeps serving the stale copy for its own
# full duration on top of s-maxage, so a low s-maxage alone doesn't bound
# staleness.
STALE_WHILE_REVALIDATE_NONE = 0

# Kept from the pre-existing headers on the preview endpoints: browsers may reuse
# a response for a minute, which is well inside any edit-then-reload window.
BROWSER_MAX_AGE = 60


def is_anonymous_request() -> bool:
    """True when the request carries no bearer token, so no auth-state variation."""
    return not request.headers.get("Authorization")


def cache_publicly(
    response: Response,
    s_maxage: int = S_MAXAGE_DEFAULT,
    stale_while_revalidate: int = STALE_WHILE_REVALIDATE_DEFAULT,
) -> Response:
    """Mark a successful, non-personalised GET response as CDN-cacheable.

    A no-op for authenticated requests and for anything that isn't a 2xx, so
    callers can apply it without re-checking those themselves. Returns the same
    response for convenient inline use.

    Pass stale_while_revalidate=0 to omit the directive entirely, which caps how
    long a stale body can be served at s_maxage.
    """
    if not is_anonymous_request():
        return response
    if not 200 <= response.status_code < 300:
        return response

    directives = ["public", f"max-age={BROWSER_MAX_AGE}", f"s-maxage={s_maxage}"]
    if stale_while_revalidate:
        directives.append(f"stale-while-revalidate={stale_while_revalidate}")
    response.headers["Cache-Control"] = ", ".join(directives)
    return response
