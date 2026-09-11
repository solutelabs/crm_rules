# SoluteLabs CRM Rulebook (Attio)

Version 0.4 — 11 Sep 2026. Owner: Karan Shah. This file is the single source of truth for how people and tasks are classified in Attio, and what the daily triage routine is allowed to do. When a rule here and a habit in Attio disagree, fix the rule or fix the habit — don't leave both.

## 1. Who gets a record

Attio auto-creates a person for every email participant. That is fine; the job is to classify, not to prune.

Every person record must end in exactly one of two states within a day of first appearing: **classified** (a `relationship` value set) or **ignored** (`ignore` = true). Nothing stays blank.

Internal addresses (`@solutelabs.com`, `@solutelabs.us`, `@solutelabs.dev`, `@solutelab.com`) are always `ignore`.

## 2. Relationship values and when to use them

| Value | Use when |
|---|---|
| Client - Founder / Owner | Founder, owner or exec sponsor at a company we are currently billing. |
| Client POC | Day-to-day contact (PM, IT manager, ops) at a current client. |
| Past Client | Founder/owner at a company we billed before but not in the last ~6 months and no live scope. |
| Past client POC | Day-to-day contact at a past client. |
| Future Prospect | Anyone we have had a real two-way conversation with about possible work — inbound leads, referrals, outbound that replied. |
| Past Lead | A prospect that went cold or said no; keep only if worth a yearly ping. |
| Referrer | Someone who introduces us to work (partners, ex-clients, Google/AWS partner managers). |
| Vendor POC | A supplier we actually use (CodeVyasa, TechMonarch, Growfusely, accountants). Also set `ignore` = true unless someone owns the vendor relationship. |
| CWX POC | Cloudwerx-specific partner contacts. |

Vendor colleagues, cold pitches, recruiters, newsletters, SaaS notifications, event/sponsorship sales, M&A/valuation outreach, "co-founder wanted" mails: `ignore` = true, no relationship needed. Add a one-line `description` saying what the pitch was and the month, so nobody re-investigates.

## 3. Importance (1–5) — how often we reach out

Importance answers one question only: how often should we proactively reach out? Who the person is lives in `relationship`, not here.

| Score | Label | Cadence |
|---|---|---|
| 5 | High / Active | monthly |
| 4 | Good | quarterly |
| 3 | Medium | every 6 months |
| 2 | Low | yearly |
| 1 | Lowest — no outreach needed | never (explicit opt-out) |

Rules of thumb: inbound lead with a live scope = 5 (the open task carries the "ongoing" part). Prospect that paused ("next year") = 2 or 3 depending on deal size. A delivery POC we only talk to inside a project, or a settled past client, is honestly a 1. Every non-ignored person with a `relationship` must have an importance; a blank importance is a defect.

History: until 11 Sep 2026 the scale ran 1–8, with 6 = "potential lead, ongoing", 7 = "Client POC, no interaction" and 8 = "Past client, no interaction". Those were retired because they duplicated `relationship`. Migration: 6 → 5, 7 and 8 → 1. Note: deleting a select option in Attio blanks the value on every record that had it — archive instead of delete next time.

### 3a. Reconnect cadence

Relationship sets a floor; importance can only make outreach more frequent; 1 is the explicit opt-out. When a person's last interaction is older than their cadence, the triage routine proposes a reconnect task (and an email angle).

| Who | Reconnect every |
|---|---|
| Existing clients (Client - Founder / Owner, Client POC) | at least monthly |
| Past clients (Past Client, Past client POC) | at least every 6 months |
| Importance 5 | monthly |
| Importance 4 | quarterly |
| Importance 3 | every 6 months |
| Importance 2 | yearly |
| Importance 1, or `ignore` | never — even if the relationship floor would say otherwise |

The shorter of the relationship floor and the importance interval applies, except that 1 always wins. The reconnect task goes to the thread owner (section 5) with the cadence date as its deadline.

### 3b. Re-review of classified people

Classification is not permanent. A relationship can change (prospect becomes client, client goes quiet, vendor becomes referrer). The triage routine may re-surface an already-classified person for review, but **only if the classification is at least 30 days old**, and only when something has changed since — a new thread, a deal stage change, or a cadence overdue by more than one interval. Re-reviews are proposed in the same table as new people, clearly marked "re-review", and follow the same stop-and-wait rule before any change.

## 4. Tasks

- Every non-ignored person with importance ≥ 2, or any open conversation, has **exactly one** open task. Not zero, not three. Importance 1 needs no task.
- Task text is self-contained: who, company, what the next step is, and any date already agreed. Someone reading only the task should know what to do.
- Assignee = whoever is driving the thread: the colleague who sent the last message or owns the deal; Karan otherwise.
- Default deadline 7 days. Paused prospects get the reconnect date the prospect gave (or +6 months), not a placeholder.
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
2. Propose up to 10 with tag, importance, owner and email angle — new people first, then re-reviews and overdue reconnects. **Stop and wait.** No Attio writes before Karan replies.
3. Before proposing, re-check Attio live — colleagues classify people during the day and the morning scan goes stale.
4. After approval: set relationship / importance / ignore, merge obvious duplicate person records, ensure one open task per non-ignored person, create drafts as approved, and report a short table of what changed.
5. Cold pitches with no Attio record: create the record with `ignore` = true and a one-line description so they stop resurfacing.
6. Contact enrichment from signatures: when a phone number appears in someone's email signature and is missing from their Attio record, add it to `phone_numbers` (append, never overwrite an existing number). Do the same for job title and LinkedIn URL if the record is blank. Only from the person's own signature — never from a colleague's forward or a third party's mail. This is a low-risk write and does not need the stop-and-wait step; list it in the end-of-run summary.

## 8. Hygiene checks worth running weekly

- People with `relationship` set, not ignored, and no `importance` (backfilled to zero on 11 Sep 2026; the ~90 ignored blanks were left as-is).
- People with importance ≥ 2 and no open task.
- People with importance 1 who have an open task or a recent two-way thread (probably mis-scored).
- People with more than one open task.
- Future Prospects with no email interaction in 90 days (downgrade or Past Lead).
- Duplicate people (same LinkedIn or same name at the same company).

## Changelog

- 0.4 (11 Sep 2026): importance simplified to 1–5 (6/7/8 retired, 1 renamed "No outreach needed"); cadence rule rewritten as relationship-floor + importance; task rule now applies at importance ≥ 2. All 50 non-ignored people with a relationship but no importance were scored the same day; 91 ignored blanks left alone.
- 0.3 (11 Sep 2026): triage may enrich phone / title / LinkedIn from the person's own email signature (7.6).
- 0.2 (11 Sep 2026): added reconnect cadence by relationship/importance (3a) and the 30-day re-review rule (3b); triage step 1–2 updated accordingly.
- 0.1 (11 Sep 2026): first draft from the daily triage routine.
