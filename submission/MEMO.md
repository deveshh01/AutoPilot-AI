# TalentFlow Q3: Acme's two asks, and the six engineer-weeks

Data: Acme production base, pulled once on 2026-10-30 and cached (`code/pull.py`). Latest record is 2026-08-27.
Size: 350 applications, 300 candidates, 160 interviews, 36 offers and 26 hires. Every number here comes from `code/analyze.py`; its full output is in `analysis_output.txt`.

**One caveat runs through everything.** The decisions here rest on 26 hires and 36 offers. At that size, a 95% interval is about ±15 points. I treat any difference smaller than that as "not shown".

---

## D5 — Memo (one page)

**What's true.**
1. *"Job boards bring in 26.9% of hires."* The arithmetic is right (7/26), but it doesn't support the ask. Referrals also bring in 7/26 = 26.9%, from 13 applications instead of 236. One job-board application in 33 becomes a hire (3.0%). For referrals it's more than one in two (53.8%), and 16.7% for everything that isn't a job board. Job boards are already 67% of application volume. A deeper integration buys more of the channel that converts worst.
2. *"Offer acceptance is ~72%."* This comes from 26 accepted / 36 offers. Five of those 36 are still marked **Pending**, so they count as failures without anyone having decided. Over decided offers only, the rate is **83.9% (26/31)**. Four of the five "Pending" offers already have a decision date, which means their status is stale and not a live state. One has been pending for 222 days. The board is looking at a data-hygiene artefact more than at a candidate problem.
3. **The source field can't carry a channel decision yet.** 27 applications have a "Referred By" person, but only 3 of those candidates are sourced "Referral". 38 candidate notes say "Referred internally", and only 2 of those are sourced Referral. Six people exist twice, with the same phone, name and different emails, and three of them are hires. Depending on which field you believe, referrals are 27% or 38% of hires, and job boards are 27% or 23%.

**What we're doing.** We say no to bringing job-board integration forward. We say yes to "move the acceptance number", but the first move is measuring it correctly, not changing comp. The 6 weeks go to: (1) offer lifecycle and a correct acceptance metric, (2) candidate de-duplication and application-level source attribution, (3) a referral-capture flow, since referrals are the channel the data says is underused.

**What I'd tell the VP.** "Your 26.9% is right, and so is a 26.9% from referrals that cost about 1/18th of the applications. Your 72% is closer to 84% once we stop counting undecided offers as declines. We'll ship the metric so the board sees the true number, then put the effort into the channel that actually converts."

**What I'd look at next, with more time.** Recruiter-level variation: one recruiter handles 31 applications and the other three handle 96–113 each. Whether the 90 applications dated before their candidate's "Created On" are imports or re-creations. Offers outside the requisition's salary band (7/36). A cohort view of acceptance by month once n allows it. I'd also confirm with Acme what "Pending" with a decision date means in their process. I could not verify that from the data.

---

## D1 — Verdicts on the VP's claims

| Claim | Verdict | The number that decides it |
|---|---|---|
| Job boards are the biggest channel, 26.9% of hires, so bring job-board integration forward | **Don't build. Build referral capture and source attribution instead.** | Job-board application→hire **3.0%** (7/236, CI 1.4–6.0) vs referral **53.8%** (7/13, CI 29–77). Both are 26.9% of hires. |
| Offer acceptance ~72%, get it moving | **Build something different: fix the offer lifecycle and metric first.** | **83.9%** over decided offers (26/31) vs 72.2% when 5 undecided "Pending" offers count in the denominator. |

Caveats I'd put in front of the VP:
- "Biggest channel by a wide margin" is true for **volume** (236/350 applications, 191/300 candidates). It is *not* true for hires, where job boards tie with referrals.
- The referral 53.8% rests on 13 applications. The interval is wide, 29–77%, but even its lower bound is above job boards' upper bound of 6%. The direction is solid. The size isn't.
- Even with my corrected number, acceptance can't be split by cause. There are only 5 declines (3 counter-offer, 1 location, 1 compensation). Offers below the candidate's expected CTC are accepted at the same rate as offers above it (83% vs 84%). Nothing here points to comp as the lever.

## D2 — The 6 engineer-weeks

**Build, in order**

| # | What | Size | The number that justifies it |
|---|---|---|---|
| 1 | **Offer lifecycle + acceptance metric.** Make `Decision On` and `Status` consistent (setting a decision date requires Accepted/Declined). Auto-expire offers past their response deadline to `Expired`. Ship the D3 metric with a "pending" band on the dashboard. | 1.5 wk | 4 of 5 Pending offers already have a decision date; one is 222 days old. Fixing this moves the reported number from 72% to ~84% with no change to candidate behaviour. |
| 2 | **Candidate identity + application-level source.** Dedupe on phone/email at create time and merge the existing duplicates. Store source per application. A filled `Referred By` takes precedence over the candidate-level source. | 2 wk | 6 people duplicated (12 records, 24 applications, 3 hires). 24 of 27 referred applications are labelled as another source. Referral hire share swings 27%→38% depending on the field. |
| 3 | **Referral capture flow.** Employees submit a referral directly, and it's tagged at source and shown to the recruiter. | 2 wk | Referral application→hire is 53.8% vs 3.0% for job boards, with only 13 referral applications, so volume is the constraint. |
| — | Buffer / data-validation checks (unique Application ID, req status vs hires) | 0.5 wk | 4 duplicate Application IDs; 7 requisitions whose hire count contradicts status/headcount. |

**Not building**

| What | Why not |
|---|---|
| **Job-board integration brought forward** | It adds volume to the lowest-converting channel, which is already 67% of applications and the main load on screening. Revisit if job-board conversion improves, or if Acme's constraint turns out to be top-of-funnel volume, which this data doesn't show. |
| **Comp / counter-offer tooling to "move acceptance"** | Only 5 declines exist. Below-expectation offers are accepted at the same rate as the rest (83% vs 84%). It's too small and too flat to act on; I'd re-check after two more quarters of clean data. |
| **Interview scorecard / process rework** | The interview data is the most internally consistent in the base. Scores line up with recommendations (Strong No Hire averages 1.5, Strong Hire 4.5), and every hire has interviews. Nothing in the data points to a problem here. |

## D3 — Metric spec: Offer Acceptance Rate

**Definition.** Of the offers whose outcome is known and that were extended in the window, the share the candidate accepted.

- **Unit:** one offer record. If a candidate gets a revised offer for the same application, only the **latest** offer per application counts. Earlier versions are superseded, not declined.
- **Cohort / time window:** offers by `Offered On` date falling in the reporting period (default: rolling 90 days, also by calendar quarter). Cohort by offer date, not decision date, so a quarter's number doesn't shift because of when people decide.
- **Numerator:** offers in the cohort with `Status = Accepted`.
- **Denominator:** offers in the cohort with `Status ∈ {Accepted, Declined, Expired}`.
- **Excluded from both:**
  - `Pending` offers still inside their response window.
  - `Rescinded` (withdrawn by Acme). This is reported separately, because a company-side withdrawal is not a candidate decline.
  - Offers on requisitions cancelled before the decision.
  - Test records and records whose application is a known duplicate.
- **Edge cases:**
  - *Pending past its deadline* (default 14 days after `Offered On` if no explicit deadline): count as `Expired`, which means in the denominator and not accepted.
  - *Has `Decision On` but status Pending:* this is a data error. Exclude it from both, and count it in the "data issues" figure.
  - *Accepted then reneged before start:* stays Accepted here. Track it in a separate "offer→join rate".
  - *Same person, two applications, two offers:* each application counts once.
- **Dashboard:**
  - Show the rate with its n and a 95% interval.
  - Show a grey "unresolved" band: the rate if all live pendings accept, and if all decline.
  - Suppress the headline and show "insufficient data" when the denominator is under 20.
  - Show the count of excluded data-error offers next to it.
  - Today's band would read: **83.9% (n=31, 67–93%); unresolved range 72–86%; 4 offers with status/date conflict.**

## D4 — What I wouldn't trust in this data

How I looked: every table was profiled field by field (fill rate, distinct values). Then I checked six things systematically:

- uniqueness of IDs and people
- referential and temporal consistency (dates in order, child after parent)
- state consistency (stage vs status vs dates vs linked records)
- cross-field agreement (source vs referred-by vs notes, salary vs band)
- aggregates vs declared capacity (hires vs headcount)
- sensitivity of each headline number to the problems found

| Problem | How much | Effect on my answers |
|---|---|---|
| **Source mislabelled.** `Referred By` set but candidate source ≠ Referral; notes say "Referred internally" on non-referral sources | 24/27 referred applications; 36/38 "referred" notes | Referral is undercounted, which makes my D1 verdict on job boards *stronger*, but I can't give an exact referral share (27–38%). |
| **Duplicate people.** Same name and phone, different email; usually one Job Board record plus one Referral or Job Board record | 6 people, 12 records, 24 applications, 3 hires | Inflates job-board applications. Two of the 7 referral hires are people who also have a job-board record, so attribution is ambiguous in both directions. |
| **Duplicate Application IDs.** The same ID is used by different people and openings | 4 IDs, 8 records | You can't key on Application ID. I keyed on the Airtable record id. |
| **Stale offer status.** Pending with a decision date | 4/5 Pending | This is the main reason 72% is understated (D1/D3). |
| **Hires contradict requisitions.** Cancelled reqs with hires, "Filled" reqs with 0 hires, hires above headcount | 7 of 24 reqs | Req status can't be used for time-to-fill or a capacity view. It doesn't affect the two claims. |
| **Applied before the candidate record was created** | 90/350 applications (26%) | `Created On` is not a reliable "first seen" date. Don't use it for source-cohort timing. |
| **Applied before the opening opened** | 3 applications | Minor; probably req reopened or back-dated. |
| **Rejection reason on non-rejected applications** | 14 Withdrawn, 2 Hired, 1 Interview, 1 Offer | Rejection-reason analysis would need cleaning first. |
| **Offer date differs between Applications and Offers tables** | 3/36 | Use the Offers table as the source of truth. |
| **Offers outside the req's salary band**, some with non-round amounts (e.g. 2,258,706) | 7/36 | This looks like data entry or currency conversion. I didn't use comp for decisions partly because of this. |
| **Scores recorded on No-Show/Cancelled interviews** | 4/160 | Small; exclude them from score analysis. |
| **Small n overall** | 26 hires, 36 offers, 5 declines | It's the biggest limit. Treat every split below the channel level as anecdotal. |

What checked out (and so I *do* trust): stage dates are always in order (0 violations), every Hired application has an accepted offer and vice versa, every Hired application has interviews, Closed/Active status matches Closed On, and scores agree with recommendations.

**What I'd check with more time:**
- Ask Acme how "Source" is set (a form default? the first touch?). The 64% Job Board share may itself partly be a default.
- Whether the 90 back-dated applications are a migration.
- Re-run once the duplicates are merged.
