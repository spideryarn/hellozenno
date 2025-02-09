from flask import (
    Blueprint,
    abort,
    jsonify,
    redirect,
    request,
    session,
    url_for,
    send_file,
)
from google_auth_oauthlib.flow import Flow

# from google.oauth2.credentials import Credentials

from utils.flask_view_utils import full_url_for
from config import GOOGLE_CLIENT_CREDENTIALS


# Create a Blueprint for our API routes
google_oauth_bp = Blueprint("google_oauth", __name__, url_prefix="/")


@google_oauth_bp.route("/google_oauth_login")
def google_oauth_login():
    # session.clear()
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
        redirect_uri=url_for("google_oauth2callback", _external=True),
    )
    print(f"{flow.redirect_uri=}")
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@google_oauth_bp.route("/oauth2callback")
def google_oauth2callback():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
        state=session["state"],
        # access_type="online",
        redirect_uri=url_for("google_oauth2callback", _external=True),
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    # Store or use the credentials to access Google Sheets API
    return "Authentication successful!"
