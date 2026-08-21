# Website Launch — Yarddogs Commercial

Campaign announcing the relaunch of **yarddogcommercial.com** to the Midlands
commercial property-management market.

- **HubSpot campaign ID:** 581439626041
- **Campaign URL:** https://app.hubspot.com/marketing/51657317/campaigns/22eb0e01-1471-41ba-8e6a-abd2ba62c37d
- **Run dates:** 2026-08-21 → 2026-09-30

## Goal

Drive Midlands property managers to the new yarddogcommercial.com and generate
"walk my property" estimate requests, establishing the site as the primary
inbound channel for commercial grounds contracts.

## Audience

Commercial property managers, HOA boards, apartment community managers, retail
center and office park decision-makers in Columbia, SC and the surrounding
Midlands (Lexington, Irmo, Blythewood, Aiken).

## Assets

| Asset | Type | ID | Status |
|---|---|---|---|
| Yarddogs Landscaping – Home | Site page | 580068821007 | Attached |
| Yarddogs Landscaping – Apparel | Site page | 581432971919 | Attached |
| Yarddogs Landscaping – Contact | Site page | 580069119085 | Attached |
| Website Launch Announcement — Aug 2026 | Marketing email | — | Blocked, see below |
| Launch blog post | Blog post | — | Blocked, see below |

## Recipients

349 contacts — every contact that is both a marketing contact and has an email
address (362), less 13 excluded addresses.

### Excluded addresses

Vendor portals, system/automation mailboxes, and internal accounts. Contact
records were left untouched; these are send-time exclusions only.

| Contact ID | Address | Reason |
|---|---|---|
| 232503985153 | qbo@intuit.com | Vendor system mailbox |
| 232480342625 | michael_wootan@intuit.com | Vendor |
| 232509228691 | dd-69c2ef33e4dbd60021b29e42@apollomailtester.com | Apollo deliverability test address |
| 232494522917 | giversgain@bni.com | Generic org mailbox |
| 232505131347 | lafayecustomhomes@buildertrend.com | Vendor portal relay |
| 232479724808 | password-reset@buildertrend.com | Automated system address |
| 232509691402 | agy_eft@agy.com | Banking/EFT mailbox |
| 232511395215 | woinvoices@pmsolutionssc.com | Invoices-only mailbox |
| 232480960019 | ucbiinvoicecapture@concursolutions.com | Invoice capture automation |
| 232488478008 | invoices@trideltaeo.org | Invoices-only mailbox |
| 232512946503 | ross@yardddogcommercial.com | Misspelled domain — will hard bounce |
| 232511553409 | ross.wigington@salesxecution.com | Internal |
| 232505924273 | michael@scarrgroup.com | Internal (portal user) |

## Email settings

| Field | Value |
|---|---|
| Internal name | Website Launch Announcement — Aug 2026 |
| From name | Taylor at Yarddogs Landscaping |
| Reply-to | taylor@yarddogcommercial.com |
| Subscription type | Marketing Information (2993505539) |
| Email type | BATCH |
| Template | @hubspot/email/dnd-wireframe/wireframe-announcement.html |
| Preview text | Grounds care, hardscape, and exterior cleanup for Midlands properties — all in one place. |

### A/B subject lines

- **A:** One crew, one invoice — see the new Yarddogs site
- **B:** We rebuilt our site for the people who manage properties

A leads with the operational benefit; B leads with the audience. Split evenly,
pick the winner on click-through rather than open rate.

## Blocked items

**Marketing email could not be created.** Every write through
`manage_marketing_email` fails with an OAuth error:

```
Protected resource https://mcp.hubspot.com does not match expected
https://api.anthropic.com/v2/ccr-sessions/.../mcp?mcp_url=...
```

Reads on the same tool succeed (from addresses, subscription types, templates),
and campaign writes succeed, so this is scoped to the marketing-email write
permission on the HubSpot connector rather than a general outage. Reconnecting
HubSpot under claude.ai Settings → Connectors should restore it. Copy for the
email is in `email-copy.md`, ready to paste.

**Blog post could not be created.** No blog exists in portal 51657317 —
`LIST_BLOGS` returns an empty list. A blog has to be created under HubSpot
Settings → Content → Blog before any post can be written to it.
