# Yarddogs — HubSpot launch tasks

Two launch tasks, run against a **HubSpot private app** rather than the chat
connector: Task A converts 26 contacts to Marketing Contact status, Task B
creates the launch announcement email as a draft.

Both scripts are **dry run by default** and print exactly what they will send.
Nothing reaches the live CRM until you pass `--execute` and confirm.

---

## One correction to the original plan

The plan's Task A used
`POST /crm/v3/objects/contacts/batch/update` with `hs_marketable_status: "true"`.
**That call cannot succeed**, and not because of scopes:
`hs_marketable_status` is a **read-only property** in the CRM API, so the batch
update returns *"read only property; its value cannot be set"* for any token,
private app or otherwise. Adding `marketable-contacts-write` would not have
fixed it either.

The supported programmatic path is the **Imports API** with
`marketableContactImport: true`, which is what `task_a_set_marketing_contacts.py`
now does. HubSpot documents three ways to set existing contacts as marketing:
the import (used here), a workflow, and bulk selection in the UI.

**If you want this done in the next 60 seconds, use the UI instead** — it is the
same operation with no token required:

> Contacts → select the 26 records → **More** → **Set as marketing contacts** →
> type the count → confirm.

The script exists for repeatability and for the before/after verification it
prints. Either path is legitimate; the UI one is faster for a one-off.

---

## Step 0 — Create the private app

HubSpot → **Settings (gear) → Integrations → Private Apps → Create a private app**.
Name it `yarddogs-claude-code-launch`.

Enable these scopes:

| Scope | Needed for |
|---|---|
| `crm.objects.contacts.read` | reading current marketing status (before/after check) |
| `crm.objects.contacts.write` | contact updates |
| `crm.import` | **Task A** — the marketing-contact import |
| `marketing-email` | **Task B** — creating the email draft |

If `marketing-email` is not offered, search the scope list for `content` — older
portals expose the marketing email API under that name.

Create the app and copy the access token.

### Handling the token

The token has real write access to your live CRM. Treat it like a password.

```bash
export HUBSPOT_PRIVATE_APP_TOKEN='pat-na1-...'
```

Set it in your shell, not in a file in this repo. Nothing here writes the token
to disk or prints it, and `.gitignore` covers `.env` in case you use one. If it
ever leaks, rotate it from the same private app settings page.

---

## Setup

```bash
pip install -r requirements.txt
```

## Task A — convert 26 contacts

```bash
python task_a_set_marketing_contacts.py                 # dry run: shows current status + the exact import payload
python task_a_set_marketing_contacts.py --execute       # runs it, after a typed confirmation
python task_a_set_marketing_contacts.py --verify-only   # just report status
```

It reads current status for all 26, aborts if any ID does not resolve, uploads a
Record-ID-only CSV as an `UPDATE` import with `marketableContactImport: true`,
polls until the import finishes, then re-reads and prints a `before -> after`
table marking every record that changed.

The 26 IDs and the two excluded HubSpot demo records live in `contacts.py`,
which raises on startup if a demo record ever appears in the target list.

## Task B — create the email draft

```bash
python task_b_create_marketing_email.py             # dry run
python task_b_create_marketing_email.py --execute   # creates the draft
```

`POST /marketing/v3/emails` only documents three required fields — `name`,
`subject`, `templatePath`. The from name, reply-to, and subscription type are
not pinned down in the public reference, so the script tries the full payload
first and falls back through smaller ones on a 400, then tells you which
settings it could not apply. Body copy is in `email_body.html`, ready to paste
into the editor with the brand colors already applied.

The script creates a **draft only**. It never schedules and never sends.

### Finish in the editor

Preview text, the logo (`Yarddogs Commercial Landscaping LogoRev1.png`, already
in the file manager), mobile rendering, and confirming the From address resolves
to `ross@yarddogcommercial.com` are all editor steps. Send is a separate,
deliberate action you take yourself.

---

## Email settings reference

| Field | Value |
|---|---|
| Internal name | Website & Apparel Launch Announcement |
| Subject | We've Launched a New Website — yarddogcommercial.com |
| Preview text | See our commercial grounds maintenance services and request a property walkthrough. |
| From name | Ross Wigington |
| From email | ross@yarddogcommercial.com |
| Reply-to | taylor@yarddogcommercial.com |
| Subscription type | Marketing Information (`2993505539`) |
| Buttons | background `#0C3721`, text `#C9B07E` |

## Sources

- [Contacts API — batch update](https://developers.hubspot.com/docs/reference/api/crm/objects/contacts)
- [Imports API — `marketableContactImport`](https://developers.hubspot.com/docs/reference/api/crm/imports)
- [Set contacts as marketing (UI, import, workflow)](https://knowledge.hubspot.com/records/set-contacts-as-marketing)
- [Marketing Emails v3 guide](https://developers.hubspot.com/docs/api-reference/marketing-marketing-emails-v3/guide)
- [`hs_marketable_status` is read-only](https://community.hubspot.com/t5/APIs-Integrations/Cannot-set-a-contact-s-marketing-status-via-API/m-p/1258011)
