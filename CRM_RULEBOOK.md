# SoluteLabs CRM Rulebook (Attio)

Version 0.5.2 — 14 Sep 2026. Owner: Karan Shah. This file is the single source of truth for how people and tasks are classified in Attio, and what the daily triage routine is allowed to do. When a rule here and a habit in Attio disagree, fix the rule or fix the habit — don't leave both.

## 1. Who gets a record

Attio auto-creates a person for every email participant. That is fine; the job is to classify, not to prune.

Every person record must end in exactly one of two states within a day of first appearing: **classified** (a `relationship` value set, and the company's `account_type` set) or **ignored** (`ignore` = true). Nothing stays blank.

`ignore` means "the triage routine never surfaces this person and nobody reaches out". It is not a softer "low priority" — that is importance 1. A person with `ignore` = true and importance ≥ 2 is a defect. Ignored people with a relationship get importance 1 by default so the field is never blank. The only relationship that is normally also ignored is Vendor (section 2).

Internal addresses (`@solutelabs.com`, `@solutelabs.us`, `@solutelabs.dev`, `@solutelab.com`) are always `ignore`.

`date_of_birth` holds the day and month only; the year is a placeholder because it is usually unknown. Don't "fix" it. A birthday note is a valid reconnect touch for anyone at importance 2 or higher.

**When a person changes employer, the client relationship stays with the old company.** Attio re-points a person to whichever company their newest email belongs to. That never makes the new employer a Customer or Past Customer. Put a one-line note on the person ("Past client via X, now at Y") and leave the new company untyped unless it becomes a client in its own right. Lesson from 14 Sep 2026: 20 companies (Korn Ferry, Intertek, HexaHealth, Medanta and others) inherited Past Customer from people who had moved.

`is_former_contact` = true means the person left that job (e.g. moved companies) and this record is their old work email. Keep the record until it is merged with the new one; it says nothing about the relationship.

**Backlog.** Roughly 11,700 people created before September 2026 have neither a relationship nor `ignore`. They are never bulk-ignored. The backlog sweep (7.7) reviews them one at a time — who they are, whether they are still a potential fit — and classifies or ignores each individually.

## 2. Relationship and account status

Two fields, two questions. **Who is this person to their company?** lives on the person as `relationship`. **What is that company to us?** lives on the company as `account_type`. Neither field repeats the other. When a client goes quiet or a prospect signs, change the company's `account_type` once; nobody re-tags people.

### 2a. Person `relationship` — the person's role

| Value | Use when |
|---|---|
| Decision Maker | Founder, owner, C-level, MD, director or exec sponsor — the person who can say yes to work or budget. |
| POC | Day-to-day contact: PM, engineering lead, IT manager, ops, finance staff. Talks to us inside a project or a deal but doesn't sign. |
| Partner | Works at a company we co-sell or subcontract with (Cloudwerx, Google/AWS partner managers, agencies that pass us work). |
| Referrer | An individual who introduces us to work in a personal capacity — ex-clients, friends, investors, founders we know. Not a company relationship. |
| Vendor | A supplier we use (CodeVyasa, TechMonarch, Growfusely, accountants) or an external contractor on a client's side. Also `ignore` = true unless someone owns the vendor relationship. |

Vendor colleagues, cold pitches, recruiters, newsletters, SaaS notifications, event/sponsorship sales, M&A/valuation outreach, "co-founder wanted" mails: `ignore` = true, no relationship needed. Add a one-line `description` saying what the pitch was and the month, so nobody re-investigates.

### 2b. Company `account_type` — the account's status

| Value | Use when |
|---|---|
| Customer | We are currently billing them or have live scope. |
| Past Customer | We billed them before; no invoice or live scope in the last ~6 months. |
| Prospect | A real two-way conversation about possible work is open or paused with a date. |
| Past Lead | A prospect that went cold or said no; keep only if worth a yearly ping. |
| Partner | Co-selling or subcontracting partner. |
| Vendor | A supplier. |

**Zoho Books is the evidence for account status and spend.** `books_reconcile.py` (read-only) sums invoices per company across all three Books entities and proposes: Customer if invoiced in the last 6 months, otherwise Past Customer; `customer_since` from the first invoice; `engagement_end_date` from the last; `total_spend_range` from the total in USD at fixed rates. It only fills blanks or raises spend, never lowers; it never re-types a Partner or Vendor, and never reopens a Past Customer that has an end date (old invoices being cleared is not new work). Karan confirms every proposed change before it is written; confirmed Books-to-Attio name mappings live in `books_overrides.json`. Run weekly.

Every company that has at least one classified person must have an `account_type`. A classified person at a company with a blank `account_type` is a defect. A person with no company (personal email, no employer known) gets a company record created from what we know, or stays `ignore`.

## 3. Importance (1–5) — how often we reach out

Importance answers one question only: how often should we proactively reach out? Who the person is lives in `relationship` and `account_type`, not here.

| Score | Label | Cadence |
|---|---|---|
| 5 | High / Active | monthly |
| 4 | Good | quarterly |
| 3 | Medium | every 6 months |
| 2 | Low | yearly |
| 1 | Lowest — no outreach needed | never. Only for people who will never work with us in any role: auditors, cold pitches, engagements that ended badly. "Quiet" is a 2, not a 1. |

Rules of thumb: Decision Maker at a Prospect with a live scope = 5 (the open task carries the "ongoing" part). Prospect that paused ("next year") = 2 or 3 depending on deal size. Decision Maker at a Past Customer or Past Lead = 2 at minimum; they might come back. A POC we only talked to inside a project can be 1 if the decision maker at that account carries the reconnect; ignored people are 1. Every person with a `relationship` must have an importance; ignored people default to 1. A blank importance is a defect.

History: until 11 Sep 2026 the scale ran 1–8, with 6 = "potential lead, ongoing", 7 = "Client POC, no interaction" and 8 = "Past client, no interaction". Those were retired because they duplicated `relationship`. Migration: 6 → 5, 7 and 8 → 1. Note: deleting a select option in Attio blanks the value on every record that had it — archive instead of delete.

### 3a. Reconnect cadence

The company's `account_type` sets a floor; importance can only make outreach more frequent; 1 is the explicit opt-out. When a person's last interaction is older than their cadence, the triage routine proposes a reconnect task (and an email angle).

| Who | Reconnect every |
|---|---|
| Decision Makers at a Customer | at least monthly |
| Decision Makers at a Past Customer | at least every 6 months |
| Decision Makers at a Past Lead | at least yearly |
| Importance 5 | monthly |
| Importance 4 | quarterly |
| Importance 3 | every 6 months |
| Importance 2 | yearly |
| Importance 1, or `ignore` | never — even if the account floor would say otherwise |

The shorter of the account floor and the importance interval applies, except that 1 always wins. POCs have no account floor; their cadence is importance alone. The reconnect task goes to the thread owner (section 5) with the cadence date as its deadline.

### 3b. Re-review of classified people

Classification is not permanent. A role can change (POC becomes the decision maker, vendor becomes a partner) and an account's status changes more often (Prospect signs, Customer goes quiet). The triage routine may re-surface an already-classified person or their company for review, but **only if the classification is at least 30 days old**, and only when something has changed since — a new thread, a deal stage change, or a cadence overdue by more than one interval. Re-reviews are proposed in the same table as new people, clearly marked "re-review", and follow the same stop-and-wait rule before any change.

## 4. Tasks

- Every non-ignored person with importance ≥ 2, or any open conversation, has **exactly one** open task. Not zero, not three. Importance 1 needs no task.
- Task text is self-contained: who, company, what the next step is, and any date already agreed. Someone reading only the task should know what to do.
- Assignee = whoever is driving the thread: the colleague who sent the last message or owns the deal; Karan otherwise.
- The task must fit the age of the thread. Check the timestamp of the last two-way exchange before writing it. Under ~30 days: continue the thread, deadline 7 days. 1–6 months: do not chase the old ask; re-open with a new angle (what changed on our side, a case study, a fresh question), deadline = the person's cadence date from the last contact. Over 6 months: treat as cold; a short reconnect, deadline = cadence date or now if already overdue. A trip (Karan travelling to their city) is a valid trigger to pull any of these forward.
- Paused prospects get the reconnect date the prospect gave (or +6 months), not a placeholder.
- When two tasks cover the same next step, keep the more detailed one, move its deadline to the earlier of the two, and complete the other. (The Attio API cannot delete tasks, so "merge" = close the duplicate.)
- Close the task when the step is done and open the next one in the same breath.

## 5. Ownership by thread

| Thread type | Default owner |
|---|---|
| Inbound via hello@ / Contact Us | Sagar Jani (first response, NDA, scheduling) — Karan joins for scoping calls |
| Existing client delivery | Prakash Donga |
| Outbound / partner development | Yash Adhiya or Sagar, whoever sent the last message |
| Founder-to-founder, referrals, investors | Karan |

## 6. Email drafts (routine-generated)

- Drafts only, never sent. From karan.shah@solutelabs.com, cc prakash.donga@solutelabs.com.
- "Hey <first name>", 3–5 short lines, plain and direct, sign-off "Cheers, Karan".
- Read the thread first; never repeat something a colleague already said.
- Prefer a fresh draft when the thread carries signature-image attachments; if a reply draft is unavoidable, flag that Karan may need to paste the text manually.
- No draft when a colleague is mid-conversation with the person unless Karan asks.

## 7. Daily triage routine — what it may and may not do

1. Scan Gmail (last ~60 days), skip internal and already-ignored people. Skip already-classified people unless they qualify for re-review under 3b or are overdue under 3a.
2. Propose up to 10 with relationship, company account type, importance, owner and email angle — new people first, then re-reviews and overdue reconnects. **Stop and wait.** No Attio writes before Karan replies.
3. Before proposing, re-check Attio live — colleagues classify people during the day and the morning scan goes stale.
4. After approval: set relationship / importance / ignore on the person, set `account_type` on the company if blank, merge obvious duplicate person records, ensure one open task per non-ignored person, create drafts as approved, and report a short table of what changed.
5. Cold pitches with no Attio record: create the record with `ignore` = true and a one-line description so they stop resurfacing.
6. Contact enrichment from signatures: when a phone number appears in someone's email signature and is missing from their Attio record, add it to `phone_numbers` (append, never overwrite an existing number). Do the same for job title and LinkedIn URL if the record is blank. Only from the person's own signature — never from a colleague's forward or a third party's mail. This is a low-risk write and does not need the stop-and-wait step; list it in the end-of-run summary.
7. Backlog sweep: in addition to the Gmail scan, take a batch of unclassified, un-ignored people from the backlog (most recent last interaction first), look at who each one is — company, title, what the threads were about — and propose classify-or-ignore per person in the same table as step 2. Same stop-and-wait rule. Batch size is whatever Karan can review that day; default 25.

## 8. Hygiene checks worth running weekly

- Books reconciliation diff (`books_reconcile.py`): any company where invoices disagree with Attio status, dates or spend.
- People with `relationship` set and no `importance` (ignored ones just get 1).
- People with `relationship` set whose company has no `account_type`, or who have no company.
- People with `ignore` = true and importance ≥ 2 (pick one).
- People with importance ≥ 2 and no open task.
- People with importance 1 who have an open task or a recent two-way thread (probably mis-scored).
- People with more than one open task.
- Prospect companies with no email interaction from anyone in 90 days (propose Past Lead).
- Customer companies with no interaction in 6 months, or an `engagement_end_date` older than 6 months (propose Past Customer). Account status changes are always proposed and confirmed by Karan, never flipped automatically.
- Duplicate people (same LinkedIn or same name at the same company).

## Changelog

- 0.5.2 (14 Sep 2026): rule added: a new employer never inherits account status from a person who moved; 20 inherited statuses cleared, real clients noted on each person, Andrew Jones re-tagged Referrer, Nethues India merged into Nethues Technologies, Elevate Learning and yBuySell recorded as Past Customers.
- 0.5.2 (14 Sep 2026): Zoho Books connected (three entities). Invoices are the evidence for `account_type`, `customer_since`, `engagement_end_date` and `total_spend_range`; the reconciliation proposes, Karan confirms. First full pass applied: 85 companies updated, NDTV merged into NDTV Profit, several Books-to-Attio mappings corrected and stored as overrides.
- 0.5.1 (12 Sep 2026): task text and deadline must match the age of the last two-way exchange (section 4); no default 7-day chase on a months-old thread. Documented `date_of_birth` as day/month only with a placeholder year.
- 0.5 (12 Sep 2026): relationship rebuilt as role-only (Decision Maker, POC, Partner, Referrer, Vendor); current/past/prospect status moved to the company's `account_type`. Reason: the old values encoded both role and status, and status was never re-tagged — only 11 of 51 "Client - Founder / Owner" people sat at a company marked Customer, "Past Client" had become a catch-all for POCs, and 122 of 284 classified people were also ignored. Migration: Client - Founder / Owner and Past Client → Decision Maker or POC by job title; Client POC and Past client POC → POC; Future Prospect and Past Lead → Decision Maker or POC by title, company set to Prospect / Past Lead; CWX POC and the Google partner managers under Referrer → Partner; Vendor POC → Vendor. Old options archived, not deleted. `ignore` redefined as exclusive with importance ≥ 2; ignored people default to importance 1 (78 backfilled). Backlog sweep added (7.7): the ~11,700 never-classified people are reviewed individually, not bulk-ignored. Account status changes are propose-only. Importance 1 narrowed to "will never work with us"; Past Lead decision makers get a yearly floor. Applied 12 Sep 2026: 284 people re-tagged (Decision Maker 161, POC 91, Vendor 29, Partner 4); 67 companies given an account_type from the old person tags; 22 companies with only weak evidence were reviewed against Gmail and set to Prospect (4), Past Customer (10) or Past Lead (10); 21 ignored-but-scored people un-ignored; 78 ignored blanks set to 1; Role in Account, Power Level, Key Contact and existing_client_poc archived on people.
- 0.4 (11 Sep 2026): importance simplified to 1–5 (6/7/8 retired, 1 renamed "No outreach needed"); cadence rule rewritten as relationship-floor + importance; task rule now applies at importance ≥ 2. All 50 non-ignored people with a relationship but no importance were scored the same day; 91 ignored blanks left alone.
- 0.3 (11 Sep 2026): triage may enrich phone / title / LinkedIn from the person's own email signature (7.6).
- 0.2 (11 Sep 2026): added reconnect cadence by relationship/importance (3a) and the 30-day re-review rule (3b); triage step 1–2 updated accordingly.
- 0.1 (11 Sep 2026): first draft from the daily triage routine.
