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
1. **Deals: 195 stage-less deals** — DONE 14 Sep 2026 (70 Won, 125 Lost "No response / went cold"). Company links fixed on ~20 deals; INR-captured-as-USD values converted at 83 INR/USD where Karan confirmed. Duplicate companies merged 14 Sep 2026 (new ids): Hello Bar -> Legion Works ccfde9b3-f4c7-4359-9236-aee219f3ecec, Coinlion -> CoinLion 7f727122-fc0e-41b6-85fd-6bfcf85bb7a9, Bqprime/NDTV Profit -> NDTV Profit b07e1e0c-576c-4bfd-aa7a-925145f74c91. Note: Attio merge creates a NEW record id; update `books_overrides.json` when a mapped company is merged.
2. **Lost-reason mapping** — DONE 14 Sep 2026: 80 deals categorised (49 Budget, 15 No response, 5 Candidate rejected [new option], 3 Timing, 3 Scope, 2 Competitor, 1 In-house, 2 Other). 294 Lost deals have no reason text and no category; left blank.
   ~~Old:~~: 82 Lost deals have free-text `lost_reason`; propose `lost_reason_category` per deal as a table, then apply.
3. **Backlog sweep batch 3**: the 38 people with importance but no relationship first, then newest unclassified. Gmail review per person, propose, wait, write; one task per account via REST.
4. **Weekly**: run `books_reconcile.py`, propose diffs; hygiene checks in rulebook §8.
5. Finance, informational: unpaid balances in Books — Launchpad $51k, CloudExperts $36k, Odds Now $33k, Amagi $17k, Roche $8.7k.

## How to resume
- `/usr/bin/python3` (the python.org build has no certs). Attio key and Zoho creds are in `.env` (gitignored).
- Re-pull live data; do not trust old CSVs. Karan reviews every write 10 at a time and answers per item.
- Pushes to `main` are blocked: branch + `gh pr create`, Karan merges.
