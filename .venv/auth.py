import os
import secrets
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode
from flask import (
    Blueprint, redirect, request, session,
    url_for, render_template
)
from app.models.user import db, User

load_dotenv()

# --------------- Blueprint ---------------
auth_bp = Blueprint("auth", __name__)

# --------------- Google OAuth Config ---------------
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

GOOGLE_AUTH_URL      = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL     = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL  = "https://www.googleapis.com/oauth2/v3/userinfo"

SCOPES = ["openid", "email", "profile"]


# --------------- Routes ---------------

@auth_bp.route("/login")
def login():
    """Render the login page."""
    return render_template("login.html")


@auth_bp.route("/login/google")
def login_google():
    """Redirect user to Google's OAuth 2.0 consent screen."""
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state

    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  url_for("auth.google_callback", _external=True),
        "response_type": "code",
        "scope":         " ".join(SCOPES),
        "state":         state,
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    return redirect(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")


@auth_bp.route("/login/google/callback")
def google_callback():
    """Handle the redirect back from Google."""
    # --- verify state ---
    if request.args.get("state") != session.pop("oauth_state", None):
        return "State mismatch – possible CSRF.", 403

    code = request.args.get("code")
    if not code:
        return "Authorization failed.", 400

    # --- exchange code for tokens ---
    token_resp = requests.post(GOOGLE_TOKEN_URL, data={
        "code":          code,
        "client_id":     GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri":  url_for("auth.google_callback", _external=True),
        "grant_type":    "authorization_code",
    })

    if token_resp.status_code != 200:
        return "Failed to obtain access token.", 500

    access_token = token_resp.json().get("access_token")

    # --- fetch user profile ---
    userinfo_resp = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if userinfo_resp.status_code != 200:
        return "Failed to fetch user info.", 500

    userinfo = userinfo_resp.json()
    email   = userinfo.get("email")
    name    = userinfo.get("name", email)
    picture = userinfo.get("picture", "")

    # --- create or fetch user in DB ---
    user = User.query.filter_by(email=email).first()
    is_new_user = user is None

    if is_new_user:
        user = User(
            name=name,
            email=email,
            role=0,                     # 0 = role not yet selected
        )
        db.session.add(user)
        db.session.commit()
    else:
        # Update name/picture from Google in case they changed
        user.name = name
        db.session.commit()

    # --- set session ---
    session["user_email"]   = email
    session["user_name"]    = user.name
    session["user_picture"] = picture

    # --- always let user pick their role ---
    return redirect(url_for("auth.select_role"))


@auth_bp.route("/select-role")
def select_role():
    """Show the role selection page after first Google sign-in."""
    if "user_email" not in session:
        return redirect(url_for("auth.login"))

    return render_template(
        "select_role.html",
        name=session.get("user_name", ""),
        email=session.get("user_email", ""),
        picture=session.get("user_picture", ""),
    )


@auth_bp.route("/select-role/<role>")
def set_role(role):
    """Save the chosen role and redirect to the matching dashboard."""
    if "user_email" not in session:
        return redirect(url_for("auth.login"))

    role_map = {"user": 1, "driver": 2}
    print(role)
    role_int = role_map.get(role)
    if role_int is None:
        return redirect(url_for("auth.select_role"))

    # Update DB
    user = User.query.filter_by(email=session["user_email"]).first()
    if user:
        user.role = role_int
        db.session.commit()

    session["user_role"] = role

    if role == "driver":
        return redirect(url_for("rider_dashboard"))
    return redirect(url_for("user_dashboard"))


@auth_bp.route("/logout")
def logout():
    """Clear session and go home."""
    session.clear()
    return redirect(url_for("home"))
