# Handoff — 14 Sep 2026

Where the CRM cleanup stands and what happens next. Written before a session reset; the rulebook (`CRM_RULEBOOK.md`) is the rules, this is the to-do.

## State
- Rulebook 0.5.3 is on PR #4 (awaiting merge). PRs #1–#3 merged.
- Attio: relationship is role-only (Decision Maker / POC / Partner / Referrer / Vendor); status on company `account_type`. 12 Customers, ~139 Past Customers, 108 Prospects, 31 Past Leads.
- Zoho Books (3 entities, DC com) connected via `zoho.py`; `books_reconcile.py` is read-only and proposes; confirmed name mappings in `books_overrides.json`. Full first pass applied (85 companies).
- 20 companies that had inherited Past Customer from people who changed jobs were cleared; the real client is noted on each person's description.
- Archived attributes: people — Role in Account, Power Level, Key Contact, Existing Client POC, Company (POC), Postal Address, Meeting Mode; companies — Industry, Location, POC, Account Tier, Strategic Value, Potential Revenue this Year; deals — Deal Won Date. New: deals `lost_reason_category` select.
- Backlog sweep: 50 people done (batches 1–2). 344 no-reply outbound contacts from 2020–25 ignored.
- Zargoza / Davis Baker flagged as cheque fraud; deal moved to Lost.

## Pending, in order
1. **Deals: 195 stage-less deals** (all imported 28 Apr 2025), 10 at a time, newest first. Rule of thumb: company is a Books customer → Won; no company, no invoice → Lost, "No response / went cold". Batch 1 proposed, not yet answered:
   | # | Deal | Value | Company | Proposal |
   |---|---|---|---|---|
   | 1 | uBuild - Launchpad | $0 | Launchpad App Development | Won |
   | 2 | iOS Devs - Dedicated | $0 | Ivy Mobility | Won |
   | 3 | iOS Developer - Heady | $0 | – | Lost |
   | 4 | iOS Automation QA - Wire | $12,000 | Wire | Won |
   | 5 | Zypp DevOps | $25,000 | – | Lost |
   | 6 | Ziphii App | $20,000 | Ziphii | Won |
   | 7 | Yash - Ivy - TL position | $40,300 | Ivy Mobility | Won |
   | 8 | WorkOnGrid OCR App | $300,000 | – | Lost |
   | 9 | Vrize RoR Devs | $24,000 | – | Lost |
   | 10 | Volvo - Flutter Developers | $0 | – | Lost |
2. **Lost-reason mapping**: 82 Lost deals have free-text `lost_reason`; propose `lost_reason_category` per deal as a table, then apply.
3. **Backlog sweep batch 3**: the 38 people with importance but no relationship first, then newest unclassified. Gmail review per person, propose, wait, write; one task per account via REST.
4. **Weekly**: run `books_reconcile.py`, propose diffs; hygiene checks in rulebook §8.
5. Finance, informational: unpaid balances in Books — Launchpad $51k, CloudExperts $36k, Odds Now $33k, Amagi $17k, Roche $8.7k.

## How to resume
- `/usr/bin/python3` (the python.org build has no certs). Attio key and Zoho creds are in `.env` (gitignored).
- Re-pull live data; do not trust old CSVs. Karan reviews every write 10 at a time and answers per item.
- Pushes to `main` are blocked: branch + `gh pr create`, Karan merges.
