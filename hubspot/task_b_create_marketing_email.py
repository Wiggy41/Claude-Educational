#!/usr/bin/env python3
"""Task B — create the launch announcement as a DRAFT marketing email.

POST /marketing/v3/emails documents only three required fields (name, subject,
templatePath). The richer settings — from name, reply-to, subscription type —
are not pinned down in the public reference, so this script degrades: it tries
the full payload first, and on a 400 falls back to progressively smaller ones,
then tells you exactly which settings it could not apply so you can finish them
in the editor.

This only ever creates a draft. It never schedules or sends.
"""

import argparse
import json
import pathlib

from hubspot_client import HubSpotError, call, confirm, describe, preflight, session, token_info

REQUIRED_SCOPES = ["marketing-email"]
TEMPLATE_PATH = "@hubspot/email/dnd/welcome.html"
SUBSCRIPTION_ID = 2993505539

NAME = "Website & Apparel Launch Announcement"
SUBJECT = "We've Launched a New Website — yarddogcommercial.com"
PREVIEW = "See our commercial grounds maintenance services and request a property walkthrough."
FROM_NAME = "Ross Wigington"
FROM_EMAIL = "ross@yarddogcommercial.com"
REPLY_TO = "taylor@yarddogcommercial.com"


def payload_variants():
    """Most complete first. Each entry: (label, body, settings it adds)."""
    minimal = {"name": NAME, "subject": SUBJECT, "templatePath": TEMPLATE_PATH}

    with_state = dict(minimal, state="DRAFT")

    full = dict(
        with_state,
        subscriptionDetails={"subscriptionId": SUBSCRIPTION_ID},
        **{"from": {"fromName": FROM_NAME, "replyTo": REPLY_TO, "fromEmail": FROM_EMAIL}},
    )
    full["subject"] = SUBJECT
    full["previewText"] = PREVIEW

    return [
        ("full", full, []),
        ("no-preview-text", {k: v for k, v in full.items() if k != "previewText"}, ["preview text"]),
        ("state only", with_state, ["preview text", "from name / reply-to", "subscription type"]),
        ("minimal", minimal, ["preview text", "from name / reply-to", "subscription type", "draft state"]),
    ]


def create_email(sess, execute, assume_yes):
    variants = payload_variants()
    print("Will attempt this payload first:\n")
    print(json.dumps(variants[0][1], indent=2))

    if not confirm(execute, assume_yes, f"create the DRAFT marketing email '{NAME}'"):
        return None, []

    attempts = []
    for label, body, unapplied in variants:
        print(f"\nAttempting: {label}")
        resp = sess.post(
            "https://api.hubapi.com/marketing/v3/emails", json=body, timeout=60
        )
        if resp.status_code < 400:
            print(f"  created ({resp.status_code})")
            return resp.json(), unapplied
        print(f"  HTTP {resp.status_code}")
        attempts.append((label, resp.status_code, describe(resp)))

    print("\nEvery payload variant was rejected:")
    for label, code, body in attempts:
        print(f"\n--- {label} (HTTP {code}) ---\n{body[:1200]}")
    raise SystemExit(
        "\nNo draft was created. Most likely the token is missing the 'marketing-email' "
        "(or 'content') scope, or the portal tier does not include the marketing email API."
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--execute", action="store_true", help="actually create the draft")
    ap.add_argument("--yes", action="store_true", help="skip the interactive confirmation")
    args = ap.parse_args()

    sess = session()
    preflight(sess, REQUIRED_SCOPES)

    email, unapplied = create_email(sess, args.execute, args.yes)
    if not email:
        return

    email_id = email.get("id")
    info = token_info(sess) or {}
    hub_id = info.get("hubId")

    print(f"\nDraft created. id={email_id}")
    if hub_id:
        print(f"Edit it: https://app.hubspot.com/email/{hub_id}/edit/{email_id}/content")

    body_file = pathlib.Path(__file__).with_name("email_body.html")
    print("\nFinish in the HubSpot editor:")
    print(f"  1. Paste the body copy from {body_file.name} into the email's rich-text module.")
    print("  2. Add the logo: 'Yarddogs Commercial Landscaping LogoRev1.png' (already in the file manager).")
    print("  3. Confirm the buttons render deep green #0C3721 with warm gold #C9B07E text.")
    for item in unapplied:
        print(f"  4. Set by hand — the API rejected it: {item}")
    print("  5. Confirm the From address resolves to ross@yarddogcommercial.com.")
    print("  6. Preview desktop + mobile.")
    print("\nSending is a separate, deliberate step. This script never sends.")


if __name__ == "__main__":
    try:
        main()
    except HubSpotError as exc:
        raise SystemExit(f"\nHubSpot API error:\n{exc}")
