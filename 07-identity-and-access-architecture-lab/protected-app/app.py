import base64
import hashlib
import json
import os
import secrets
from functools import wraps
from urllib.parse import urlencode

import jwt
import requests
from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-development-secret-change-me")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # localhost uses HTTP in this lab only
)

KEYCLOAK_BASE = os.environ.get("KEYCLOAK_BASE", "http://localhost:8080" ).rstrip("/")
REALM = os.environ.get("KEYCLOAK_REALM", "cloudsec")
CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "security-console")
REDIRECT_URI = os.environ.get("OIDC_REDIRECT_URI", "http://localhost:8000/callback" )
POST_LOGOUT_REDIRECT_URI = os.environ.get(
    "OIDC_POST_LOGOUT_REDIRECT_URI", "http://localhost:8000/"
 )
ISSUER = f"{KEYCLOAK_BASE}/realms/{REALM}"
DISCOVERY_URL = f"{ISSUER}/.well-known/openid-configuration"

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }} · CloudSec Identity Lab</title>
  <style>
    :root {
      --bg: #10131b; --panel: #171c27; --panel2: #202737;
      --line: #30394c; --text: #e9edf5; --muted: #a9b3c7;
      --violet: #9a8cff; --teal: #42d3c4; --amber: #f2c66d;
      --red: #f07178; --green: #76e3a5;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--text); font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }
    .shell { max-width: 1100px; margin: 0 auto; padding: 28px; }
    .top { display: flex; justify-content: space-between; gap: 20px; align-items: center; border-bottom: 1px solid var(--line); padding-bottom: 18px; }
    .brand { color: var(--violet); letter-spacing: .12em; font-weight: 800; }
    .tag { color: var(--muted); font-size: 12px; margin-top: 8px; }
    .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 22px; margin-top: 22px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
    .card { background: var(--panel2); border: 1px solid var(--line); border-radius: 10px; padding: 16px; }
    .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
    .value { font-size: 18px; margin-top: 8px; overflow-wrap: anywhere; }
    .good { color: var(--green); } .info { color: var(--teal); } .warn { color: var(--amber); } .bad { color: var(--red); }
    a.button { display: inline-block; padding: 11px 15px; border-radius: 8px; text-decoration: none; color: #10131b; background: var(--teal); font-weight: 800; margin: 5px 5px 0 0; }
    a.button.secondary { background: var(--violet); } a.button.warn { background: var(--amber); }
    a.button.dark { color: var(--text); background: var(--panel2); border: 1px solid var(--line); }
    pre { background: #0b0e14; border: 1px solid var(--line); padding: 16px; border-radius: 8px; overflow: auto; color: #d8e0ef; }
    code { color: var(--teal); }
    h1, h2, h3 { margin-top: 0; } h1 { font-size: 26px; } h2 { font-size: 18px; color: var(--violet); }
    .footer { color: var(--muted); border-top: 1px solid var(--line); margin-top: 28px; padding-top: 15px; font-size: 12px; }
  </style>
</head>
<body>
  <main class="shell">
    <header class="top">
      <div><div class="brand">CLOUDSEC / IDENTITY LAB</div><div class="tag">authorization · authentication · least privilege</div></div>
      {% if user %}<a class="button dark" href="{{ url_for('logout') }}">Sign out</a>{% endif %}
    </header>
    {{ body|safe }}
    <div class="footer">Local-only training application · Keycloak realm: <code>{{ realm }}</code> · Never expose this development server publicly.</div>
  </main>
</body>
</html>
"""


def page(title, body):
    return render_template_string(
        PAGE,
        title=title,
        body=body,
        user=session.get("user"),
        realm=REALM,
    )


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def create_pkce_pair():
    verifier = b64url(secrets.token_bytes(32))
    challenge = b64url(hashlib.sha256(verifier.encode("ascii")).digest())
    return verifier, challenge


def discovery():
    response = requests.get(DISCOVERY_URL, timeout=10)
    response.raise_for_status()
    return response.json()


def load_signing_key(token, jwks_uri):
    header = jwt.get_unverified_header(token)
    response = requests.get(jwks_uri, timeout=10)
    response.raise_for_status()
    keys = response.json().get("keys", [])

    for key in keys:
        if key.get("kid") == header.get("kid"):
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))

    raise RuntimeError("No matching Keycloak signing key was found")


def validate_access_token(token, metadata):
    key = load_signing_key(token, metadata["jwks_uri"])
    claims = jwt.decode(
        token,
        key=key,
        algorithms=["RS256"],
        issuer=ISSUER,
        options={"verify_aud": False},
    )

    if claims.get("azp") not in (None, CLIENT_ID):
        raise RuntimeError("Token authorized party does not match this client")

    return claims


def roles_from_claims(claims):
    return sorted(claims.get("realm_access", {}).get("roles", []))


def require_role(role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("claims"):
                return redirect(url_for("login", next=request.path))

            if role not in session.get("roles", []):
                body = f"""
                <section class='panel'><h1>Access denied</h1>
                <p class='bad'>Required role: <code>{role}</code></p>
                <p>Your token roles do not authorize this action.</p>
                <a class='button' href='{url_for('home')}'>Return to dashboard</a></section>
                """
                return page("Access denied", body), 403

            return view(*args, **kwargs)

        return wrapped

    return decorator


@app.get("/")
def home():
    if not session.get("claims"):
        body = """
        <section class='panel'>
          <h1>Protected Identity Console</h1>
          <p>Authenticate with Keycloak to view the local authorization dashboard.</p>
          <a class='button' href='/login'>Sign in with Keycloak</a>
        </section>
        <section class='panel'><h2>Architecture objective</h2>
          <p>This application demonstrates authorization-code flow with PKCE, issuer and JWKS signature validation, and role-gated routes.</p>
        </section>
        """
        return page("Sign in", body)

    claims = session["claims"]
    roles = session.get("roles", [])
    role_links = "".join(
        f"<a class='button secondary' href='{url_for('role_view', role=role)}'>Open {role}</a>"
        for role in ("security-observer", "developer", "security-admin")
        if role in roles
    )

    body = f"""
    <section class='panel'><h1>Authorization Dashboard</h1>
      <p class='good'>Authenticated and locally validated.</p>
      <div class='grid'>
        <div class='card'><div class='label'>Identity</div><div class='value'>{claims.get('preferred_username', 'unknown')}</div></div>
        <div class='card'><div class='label'>Issuer</div><div class='value'>{claims.get('iss', 'unknown')}</div></div>
        <div class='card'><div class='label'>Token subject</div><div class='value'>{claims.get('sub', 'unknown')}</div></div>
        <div class='card'><div class='label'>Expiry</div><div class='value'>{claims.get('exp', 'unknown')}</div></div>
      </div>
      <h2 style='margin-top:22px'>Granted realm roles</h2>
      <p class='info'>{', '.join(roles) if roles else 'No realm roles present'}</p>
      {role_links}
    </section>
    <section class='panel'><h2>Validated claims</h2><pre>{json.dumps(claims, indent=2)}</pre></section>
    """
    return page("Dashboard", body)


@app.get("/login")
def login():
    metadata = discovery()
    verifier, challenge = create_pkce_pair()
    session["state"] = secrets.token_urlsafe(32)
    session["code_verifier"] = verifier
    session["next_url"] = request.args.get("next", "/")

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "openid profile email",
        "redirect_uri": REDIRECT_URI,
        "state": session["state"],
        "prompt": "login",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }

    return redirect(f"{metadata['authorization_endpoint']}?{urlencode(params)}")


@app.get("/callback")
def callback():
    if request.args.get("error"):
        return (
            page(
                "Authentication error",
                f"<section class='panel'><h1>Authentication failed</h1><pre>{request.args}</pre></section>",
            ),
            400,
        )

    expected_state = session.pop("state", "")
    received_state = request.args.get("state", "")
    if not secrets.compare_digest(received_state, expected_state):
        return (
            page(
                "Invalid state",
                "<section class='panel'><h1>Invalid OIDC state</h1><p class='bad'>The callback was rejected.</p></section>",
            ),
            400,
        )

    code = request.args.get("code")
    verifier = session.pop("code_verifier", None)
    if not code or not verifier:
        return (
            page(
                "Invalid callback",
                "<section class='panel'><h1>Missing authorization code</h1></section>",
            ),
            400,
        )

    try:
        metadata = discovery()
        token_response = requests.post(
            metadata["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "code_verifier": verifier,
            },
            timeout=10,
        )
        token_response.raise_for_status()
        token_data = token_response.json()

        claims = validate_access_token(token_data["access_token"], metadata)
        session["claims"] = claims
        session["user"] = claims.get("preferred_username", "authenticated-user")
        session["id_token"] = token_data.get("id_token")
        session["roles"] = roles_from_claims(claims)
        session["token_type"] = token_data.get("token_type", "Bearer")

        return redirect(session.pop("next_url", "/"))

    except Exception as exc:
        return (
            page(
                "Token validation failed",
                f"<section class='panel'><h1>Token validation failed</h1><pre>{exc}</pre></section>",
            ),
            502,
        )


@app.get("/role/<role>")
def role_view(role):
    if not session.get("claims"):
        return redirect(url_for("login", next=request.path))

    if role not in session.get("roles", []):
        return (
            page(
                "Access denied",
                f"<section class='panel'><h1>Access denied</h1><p class='bad'>The current identity does not have <code>{role}</code>.</p></section>",
            ),
            403,
        )

    body = f"""
    <section class='panel'><h1>Role workspace: {role}</h1>
      <p class='good'>Authorization decision: ALLOW</p>
      <p>This page is protected by a server-side role check after validating the Keycloak access-token signature and issuer.</p>
      <a class='button' href='{url_for('home')}'>Back to dashboard</a>
    </section>
    """
    return page(role, body)


@app.get("/observer")
@require_role("security-observer")
def observer():
    return role_view("security-observer")


@app.get("/developer")
@require_role("developer")
def developer():
    return role_view("developer")


@app.get("/admin")
@require_role("security-admin")
def admin():
    return role_view("security-admin")


@app.get("/logout")
def logout():
    id_token = session.get("id_token")
    session.clear()

    try:
        metadata = discovery()
        params = {
            "client_id": CLIENT_ID,
            "post_logout_redirect_uri": POST_LOGOUT_REDIRECT_URI,
        }

        if id_token:
            params["id_token_hint"] = id_token

        logout_url = f"{metadata['end_session_endpoint']}?{urlencode(params)}"
        return redirect(logout_url)

    except Exception:
        return redirect(POST_LOGOUT_REDIRECT_URI)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
