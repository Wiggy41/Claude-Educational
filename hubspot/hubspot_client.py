"""Shared helpers for talking to HubSpot with a private-app token.

The token is read from the environment only. It is never logged, never written
to disk, and never included in an error message.
"""

import json
import os
import sys

import requests

API_BASE = "https://api.hubapi.com"
TOKEN_ENV = "HUBSPOT_PRIVATE_APP_TOKEN"


class HubSpotError(RuntimeError):
    """An API call came back 4xx/5xx."""


def get_token():
    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        sys.exit(
            f"{TOKEN_ENV} is not set.\n"
            f"  export {TOKEN_ENV}='pat-na1-...'\n"
            "See README.md for how to create the private app and copy its token."
        )
    return token


def session():
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {get_token()}"})
    return s


def describe(resp):
    """Readable failure body, without echoing anything we sent."""
    try:
        body = resp.json()
    except ValueError:
        return resp.text[:2000]
    return json.dumps(body, indent=2)[:4000]


def call(sess, method, path, **kwargs):
    resp = sess.request(method, API_BASE + path, timeout=60, **kwargs)
    if resp.status_code >= 400:
        raise HubSpotError(f"{method} {path} -> HTTP {resp.status_code}\n{describe(resp)}")
    return resp


def token_info(sess):
    """Best-effort scope readout for the private-app token.

    Used as a preflight so a missing scope surfaces before we start writing
    rather than halfway through. Returns None if the endpoint is unavailable.
    """
    try:
        resp = sess.post(
            f"{API_BASE}/oauth/v2/private-apps/get/access-token-info",
            json={"tokenId": get_token()},
            timeout=30,
        )
        if resp.status_code >= 400:
            return None
        return resp.json()
    except requests.RequestException:
        return None


def preflight(sess, required_scopes):
    """Print hub identity and warn about scopes that look missing."""
    info = token_info(sess)
    if not info:
        print("! Could not read token info — skipping the scope preflight.")
        print("  (Not fatal. The call below will fail with a scope error if one is missing.)\n")
        return
    hub_id = info.get("hubId")
    scopes = set(info.get("scopes") or [])
    print(f"Portal (hubId): {hub_id}")
    print(f"Token scopes:   {len(scopes)} granted")
    missing = [s for s in required_scopes if s not in scopes]
    if missing:
        print(f"! Possibly missing scopes: {', '.join(missing)}")
        print("  HubSpot scope names vary by account tier; if the call still works, ignore this.\n")
    else:
        print("All required scopes present.\n")


def confirm(execute, assume_yes, action):
    """Gate every write. Dry run is the default."""
    if not execute:
        print(f"\nDRY RUN — nothing was sent to HubSpot.\nRe-run with --execute to: {action}")
        return False
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        sys.exit("\n--execute needs confirmation. Re-run with --yes in a non-interactive shell.")
    print(f"\nAbout to: {action}")
    print("This writes to the LIVE CRM.")
    return input("Type 'yes' to continue: ").strip().lower() == "yes"
