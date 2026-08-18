"""Vetted contact list for the Yarddogs marketing-contact conversion.

Sourced from the launch plan. Names are carried alongside the IDs so dry-run
output is human-checkable before anything is written to the live CRM.
"""

# (record_id, name) — 26 real contacts to convert.
CONTACTS = [
    ("232991530844", "Tim Moore"),
    ("232964940818", "James Lipscomb"),
    ("232926638854", "Ron Pagotta"),
    ("232926258252", "Tim Moore (duplicate record)"),
    ("232933056437", "Todd Lyle"),
    ("234048563515", "Half Moon Property Management"),
    ("234958377323", "Bridge Homes"),
    ("236802941228", "Tara Rogers"),
    ("236676021668", "Mike Dixon"),
    ("232737517170", "Cullen Dalton"),
    ("235672753818", "Kyle Crown"),
    ("235672757931", "Rob Peltier"),
    ("235237497715", "Christa Collins"),
    ("236419730260", "Pamela Butler"),
    ("238987829113", "Dee Robert's"),
    ("241015359586", "Mickey Laws"),
    ("237441744917", "Blake Cross"),
    ("237441744922", "Tim McCullough"),
    ("235672820088", "Wayne Redding"),
    ("232991688033", "Billy Cantey"),
    ("241295179067", "Bill W"),
    ("241286085888", "NAI Columbia"),
    ("242055622583", "Courtney Sanders"),
    ("242055502652", "Crystal Mcclam"),
    ("241286083160", "Trinity Partners"),
    ("242056182346", "Dan Geist"),
]

# HubSpot demo records. Never include these in any write.
EXCLUDED = {
    "230935291153": "Maria Johnson (Sample Contact)",
    "230947724695": "Brian Halligan (Sample Contact)",
}

CONTACT_IDS = [cid for cid, _ in CONTACTS]

# Guard against an accidental paste of a demo record into the list above.
_overlap = EXCLUDED.keys() & set(CONTACT_IDS)
if _overlap:
    raise SystemExit(f"Excluded demo contacts present in CONTACTS: {sorted(_overlap)}")
