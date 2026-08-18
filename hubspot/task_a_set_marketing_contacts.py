#!/usr/bin/env python3
"""Task A — set 26 vetted contacts to Marketing Contact status.

Why an import and not a batch property update:
`hs_marketable_status` is a read-only property in the CRM API. A
PATCH/POST to /crm/v3/objects/contacts/batch/update returns
"read only property; its value cannot be set" no matter which scopes the
token holds, so no private app can make that call work. The supported
programmatic path is the Imports API with `marketableContactImport: true`,
which is what this script uses.

Dry run by default. Nothing is written until you pass --execute.
"""

import argparse
import csv
import io
import json
import time

import contacts
from hubspot_client import HubSpotError, call, confirm, preflight, session

REQUIRED_SCOPES = ["crm.objects.contacts.read", "crm.objects.contacts.write", "crm.import"]
CONTACT_TYPE_ID = "0-1"
POLL_SECONDS = 5
POLL_TIMEOUT = 300


def read_status(sess, ids):
    """Current marketable status for each contact, keyed by record ID."""
    out = {}
    for start in range(0, len(ids), 100):
        chunk = ids[start:start + 100]
        resp = call(
            sess, "POST", "/crm/v3/objects/contacts/batch/read",
            json={
                "properties": ["hs_marketable_status", "firstname", "lastname", "email"],
                "inputs": [{"id": cid} for cid in chunk],
            },
        )
        for row in resp.json().get("results", []):
            out[row["id"]] = row.get("properties", {})
    return out


def build_csv(rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Record ID"])
    for cid, _name in rows:
        writer.writerow([cid])
    return buf.getvalue()


def import_request(name):
    return {
        "name": name,
        "importOperations": {CONTACT_TYPE_ID: "UPDATE"},
        "dateFormat": "MONTH_DAY_YEAR",
        "marketableContactImport": True,
        "createContactListFromImport": False,
        "files": [{
            "fileName": "marketing_contacts.csv",
            "fileFormat": "CSV",
            "fileImportPage": {
                "hasHeader": True,
                "columnMappings": [{
                    "columnObjectTypeId": CONTACT_TYPE_ID,
                    "columnName": "Record ID",
                    "propertyName": "hs_object_id",
                    "columnType": "HUBSPOT_OBJECT_ID",
                }],
            },
        }],
    }


def poll_import(sess, import_id):
    deadline = time.time() + POLL_TIMEOUT
    state = None
    while time.time() < deadline:
        body = call(sess, "GET", f"/crm/v3/imports/{import_id}").json()
        state = body.get("state")
        print(f"  import {import_id}: {state}")
        if state in ("DONE", "FAILED", "CANCELED"):
            return body
        time.sleep(POLL_SECONDS)
    print(f"  still {state} after {POLL_TIMEOUT}s — check the import in HubSpot's UI.")
    return {"state": state}


def print_status_table(before, after=None):
    width = max(len(n) for _, n in contacts.CONTACTS)
    for cid, name in contacts.CONTACTS:
        b = (before.get(cid) or {}).get("hs_marketable_status", "?")
        if after is None:
            print(f"  {name:<{width}}  {cid}  {b}")
        else:
            a = (after.get(cid) or {}).get("hs_marketable_status", "?")
            flag = " " if a == b else "*"
            print(f"{flag} {name:<{width}}  {cid}  {b} -> {a}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--execute", action="store_true", help="actually run the import")
    ap.add_argument("--yes", action="store_true", help="skip the interactive confirmation")
    ap.add_argument("--verify-only", action="store_true", help="just report current status and exit")
    args = ap.parse_args()

    sess = session()
    preflight(sess, REQUIRED_SCOPES)

    ids = contacts.CONTACT_IDS
    print(f"Target: {len(ids)} contacts")
    print(f"Excluded demo records: {', '.join(contacts.EXCLUDED.values())}\n")

    print("Reading current marketing status...")
    before = read_status(sess, ids)
    missing = [cid for cid in ids if cid not in before]
    if missing:
        print(f"! {len(missing)} ID(s) not found in the portal: {missing}")
        print("  Fix the list in contacts.py before running the import.\n")

    print("\nCurrent status:")
    print_status_table(before)

    already = sum(1 for cid in ids if (before.get(cid) or {}).get("hs_marketable_status") == "true")
    print(f"\n{already}/{len(ids)} already marketing contacts.")

    if args.verify_only:
        return
    if missing:
        raise SystemExit("\nAborting: some contact IDs do not resolve. Nothing was written.")
    if already == len(ids):
        print("Nothing to do.")
        return

    csv_text = build_csv(contacts.CONTACTS)
    req = import_request("Yarddogs launch — set marketing contacts")
    print("\nImport request:")
    print(json.dumps(req, indent=2))

    if not confirm(args.execute, args.yes,
                   f"set {len(ids) - already} contact(s) to Marketing Contact via the Imports API"):
        return

    print("\nUploading import...")
    resp = call(
        sess, "POST", "/crm/v3/imports",
        data={"importRequest": json.dumps(req)},
        files={"files": ("marketing_contacts.csv", csv_text, "text/csv")},
    )
    body = resp.json()
    import_id = body.get("id")
    print(f"Import created: {import_id}")

    result = poll_import(sess, import_id)
    if result.get("state") != "DONE":
        print("\nImport did not finish cleanly:")
        print(json.dumps(result, indent=2)[:2000])
        print("\nFallback: HubSpot's UI can do this directly — Contacts, select the records,")
        print("More > Set as marketing contacts. See README.md.")
        return

    print("\nRe-reading status...")
    after = read_status(sess, ids)
    print()
    print_status_table(before, after)
    converted = sum(1 for cid in ids if (after.get(cid) or {}).get("hs_marketable_status") == "true")
    print(f"\n{converted}/{len(ids)} are now marketing contacts.")
    if converted != len(ids):
        print("Some did not convert. Check the import detail in HubSpot > Contacts > Imports.")


if __name__ == "__main__":
    try:
        main()
    except HubSpotError as exc:
        raise SystemExit(f"\nHubSpot API error:\n{exc}")
