# Sending the launch email by hand

The connector cannot create marketing emails right now, so this is the manual
path. Roughly ten minutes end to end.

## 1. Build the recipient list

Hand-picking 349 contacts is not realistic, so build an active list once and
reuse it. **Contacts → Lists → Create list → Contact-based → Active.**

Name it `Marketable contacts — email known`, then add two filters:

- **Marketing contact status** *is equal to* **Marketing contact**
- **Email** *is known*

That should resolve to 362 contacts.

## 2. Create the email

**Marketing → Marketing Email → Create → Regular.** Pick the
**Announcement** drag-and-drop template.

Settings tab:

| Field | Value |
|---|---|
| Internal name | Website Launch Announcement — Aug 2026 |
| From name | Taylor at Yarddogs Landscaping |
| From/reply-to address | taylor@yarddogcommercial.com |
| Subject | One crew, one invoice — see the new Yarddogs site |
| Preview text | Grounds care, hardscape, and exterior cleanup for Midlands properties — all in one place. |
| Subscription type | Marketing Information |
| Campaign | Website Launch — Yarddogs Commercial |

Setting the campaign matters — it is what makes the send report up to the
campaign alongside the site pages.

## 3. Drop in the content

- **Logo image:** https://51657317.fs1.hubspotusercontent-na1.net/hubfs/51657317/Yarddogs%20Commercial%20Landscaping%20LogoRev1.png
- **Body:** paste `email-body.html` into a rich-text module using the source-code
  view (`</>` in the toolbar), not the visual editor, or the inline styles will
  be stripped.
- **Button module**, placed where the comment marks it in the HTML:
  text `Let's walk your property`, link `https://yarddogcommercial.com/contact`.
- Leave the default footer so the unsubscribe link stays intact.

## 4. Set recipients

Send to `Marketable contacts — email known`.

Under **Don't send to**, add these 13. They are vendor portals, automation
mailboxes, and internal accounts, and `ross@yardddogcommercial.com` has a
misspelled domain that will hard bounce:

```
qbo@intuit.com
michael_wootan@intuit.com
dd-69c2ef33e4dbd60021b29e42@apollomailtester.com
giversgain@bni.com
lafayecustomhomes@buildertrend.com
password-reset@buildertrend.com
agy_eft@agy.com
woinvoices@pmsolutionssc.com
ucbiinvoicecapture@concursolutions.com
invoices@trideltaeo.org
ross@yardddogcommercial.com
ross.wigington@salesxecution.com
michael@scarrgroup.com
```

That leaves 349 real recipients.

## 5. A/B the subject line

**Create A/B test** at the top of the editor. Version B keeps everything
identical except the subject:

> We rebuilt our site for the people who manage properties

A leads with the operational benefit, B with the audience. Split 50/50 and pick
the winner on **click-through**, not opens — Apple Mail Privacy Protection
inflates open rates enough to make them a poor signal.

## 6. Before you send

- Send yourself a test and read it on a phone. Most property managers will open
  it there.
- This is the first marketing send from this domain to a list of this size.
  If deliverability matters to you, send to a few hundred now and the rest in a
  day or two rather than all 349 at once.
- Tuesday through Thursday, mid-morning, tends to land best for this audience.
