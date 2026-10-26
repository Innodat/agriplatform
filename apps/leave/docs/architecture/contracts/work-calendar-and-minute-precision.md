# Work calendars, civil time and exact minute precision

**Status:** Technical planning candidate for the consolidated review, 2026-10-26.
**Owners:** 2.18 holiday entries; 2.19 profile representation; 2.20–2.24 effective selection;
3.7 duration; 3.18 accounting; actual E5–E8 consumers. Product rules remain Features §3/6
and accepted L-0003/0041/0074/0103. No accepted decision is rewritten.

## Canonical schedule and closure shapes

A weekly working day has one mode: net_minutes or advanced_intervals. Net is an integer
0–1440 minutes excluding breaks. Advanced uses integer minute-of-civil-day half-open
work intervals [start,end), 0 <= start < end <=1440, with disjoint work intervals and
break intervals entirely within work. Breaks cannot overlap; reject duplicate/overlapping
inputs rather than subtract twice. Cross-midnight work is explicitly split onto adjacent
civil days in the weekly editor. Adjacent intervals may touch. Advanced derives the net
length of work minus breaks; net is read-only in Advanced, not a conflicting second input.
Switching to net discards interval detail only after explicit review; net-to-Advanced
requires entered intervals and never fabricates a start time. Existing history remains.

One effective calendar closure exists per calendar/civil date, keyed uniquely in that
calendar version. It has labels/observed-date provenance and one closed shape:
full_day; reduction_minutes (positive integer <=1440); or clock_intervals (nonoverlapping
civil-minute intervals). Multiple holiday labels for that date do not multiply closure.
Conflicting same-date imports/edits require one explicitly resolved entry; no summing
unrelated duplicates, guessed substitution date or external jurisdiction law engine.

Full_day resolves to zero working minutes. reduction_minutes resolves to
max(0, scheduled net minutes - reduction). It is a duration reduction, not invented
morning/afternoon absence. clock_intervals subtract the union's intersection with actual
Advanced work after breaks. Intervals outside work have no effect; overlapping a break
never subtracts twice. Reject mixing reduction and clock modes in the same entry.
A clock closure applied to a nonzero net-only day requires Advanced detail for that date;
return work_intervals_required, not fabricated intervals, ignored closure or unavailable
service masquerading as zero. Full closure/zero work needs no interval detail.

For example, net 480 with reduction 120 gives 360; Advanced 09:00–17:00 with break
12:00–13:00 and closure 11:00–14:00 gives 300 (420 net less 120 working minutes).
A full holiday is zero regardless of duplicate labels; reduction 600 on a 480 day is zero.
The half-day request always uses half of the resulting eligible working minutes.

## Timezone, DST and effective selection

Use the effective IANA work timezone and profile/calendar versions for each requested
civil leave date. Weekly intervals represent nominal local clock working quotas: their
civil-minute length does not gain/lose minutes across a DST transition. Net and Advanced
therefore agree on the same nominal schedule. A repeated clock hour is counted once and
a skipped clock hour does not shrink the quota. This explicitly selected Leave duration
model is not elapsed-time payroll or a precise UTC shift scheduler. Existing temporary
approval appointments still use their accepted half-open UTC instant semantics.

A 01:00–04:00 Advanced quota on a spring-forward or fall-back date is 180 minutes in both
cases; half is 90. Calendar clock closures use those same civil coordinates, so closure
02:00–03:00 reduces that quota by 60 in either case. Do not ask a date-only leave request
for offset/fold or silently apply server timezone. Retain the chosen IANA name, effective
version refs, civil date and resolver/build timezone-data version in calculation evidence.
Replay uses retained resolved inputs, not a newly installed timezone database's guesses.

Effective intervals are inclusive civil dates under their recorded work timezone and
must not overlap within the selection scope. An effective timezone change governs its
new dated segment; do not convert a prior segment's date into a new date or use today's
profile for backdated leave. The earliest requested date start for L-0168 cancellation
uses current verified work timezone as that decision requires, not this nominal quota
arithmetic. UI date localization never changes canonical dates or immutable snapshots.

## Exact half-minute amounts, not integer-only consumption

Working and closure minutes remain integers. Exact 50% of an odd-minute day needs a
half-minute: 435 / 2 =217.5; 451 /2=225.5. L-0103 floors usable earned entitlement once
to whole minutes; it does not authorize rounding requests, reservations, balances or
replayed residuals. Two 217.5 halves consume exactly 435 and satisfy a 435 capacity.
Hours input remains in accepted 30-minute increments; no new request mode/increment.

Use exact fixed-point canonical minutes for duration/allocation/reservation/consumption/
reversal, relevant balance components, report amounts and imports. JSON is a string:
"0", "217.5", "435"; canonical syntax 0 or an unsigned nonzero integer, optionally .5.
Signed balance/delta fields additionally allow a leading minus on nonzero values.
No negative zero, leading zeros, exponent, comma, whitespace or binary float. Counts,
revisions, sequences and opaque membership IDs retain their integer/string contracts.

Selected storage is unconstrained PostgreSQL numeric with explicit CHECK constraints
for abs(amount) <=9999999999999999999.5 and amount * 2 = trunc(amount * 2), plus actual
nonnegative/positive/signed field constraints. Do not use a scale-limited numeric typmod
that silently rounds alternate SQL writes before the constraint sees the input. Validate
wire bounds/precision before storage as well. Use Decimal or integer half-minute
units internally, converting to canonical minutes on the wire. This is not a switch to
seconds or an extra ledger. Cross-owner JSON schemas/generated clients must distinguish
MinuteAmount from integer counters. Source entitlement fractions before their accepted
floor retain the higher precision required by L-0092/0105; this type does not truncate them.

This contract supersedes integer-only **technical candidate** amount mappings in the E3,
E6 and E7 contracts. No runtime Leave schema exists to migrate here; delivery still uses
controlled compatible migrations, actual constraints and immutable event provenance.
E5 original criteria/accepted allocation remain unchanged. Source portions preserve
integer grant entitlement plus exact half-minute reserved/consumed/remaining amounts;
never floor a 217.5 remainder to217. Allocator ordering/provenance is unchanged. E6
reverses original exact lines. E7 totals exact minutes and rounds only marked display
conversions; E8 must preserve exact source values or identify an unsupported precision
for explicit reconciliation, not silently round a .25 import to .5/0.

## Planned acceptance witnesses and ownership

2.18: full/reduction/clock shapes, unique date, overlap/break union, mode conflict and
zero saturation. 2.19: minute bounds, net/Advanced round-trip/review, no fabricated shift,
midnight split and effective versions. 3.7: mixed nonworking dates, odd-minute full/half,
30-minute input, clock closure on net-only, DST spring/fall and historical timezone.
3.18/5.6/5.8: exact allocation, two-halves capacity with concurrent submit, 435 grant minus
217.5 remainder, reversal/replay conservation, wrong wire precision and transaction
rollback. E7/E8 verify exact aggregate/export/import and unsupported-precision reporting.
These are contract-bound fixtures for existing criteria, not claimed runtime tests.

Retain 2.18/2.19/3.7 as bounded independent leaves: calendar entry representation, profile
editor/reader and pure deterministic duration respectively; later consumers extend their
actual types, not a calendar engine. Scaffold: promote proven fixed-point/interval fixtures
with first consumer. Shared UI: existing minute/time editor and accessible review/error
controls, no precise absence-time picker. Agent context: existing civil-date/ownership
rules suffice. Documentation: this contract, source adapters and actual schema/client
wire references. ADR: nominal-DST/closure/precision selections remain candidates for the
single review; no accepted ADR edited. No runtime implementation or migration performed.

## Noncircular current-time timezone selection

The initial controlled configuration has an explicit UTC applicability anchor and one
validated IANA timezone; selecting it never requires first calculating today in that
timezone. The anchor is fixture/provisioning evidence, not browser time. For subsequent
future effective-date timezone changes, interpret midnight of the reviewed effective
civil date in the predecessor's timezone, then retain that UTC boundary with both version
references. At repeated midnight choose the earliest occurrence; at a nonexistent
midnight use the first valid instant on that same civil date; reject a wholly skipped
civil date. Preview those consequences explicitly. Require strictly increasing UTC
boundaries and nonoverlapping date segments. Changes affecting an already scheduled
chain revalidate and review all affected later boundaries under existing source-impact
guards rather than silently moving them. Current-time resolution selects the version
by retained UTC interval, then calculates its business date. Dated leave calculation
selects the recorded civil-date segment and retained version, never today's timezone.
A timezone switch can change the current local date; no prior request date is rewritten.
This supplies the earlier e1-work-timezone-configuration applicability gate for consumers
which actually need timezone-dependent results. Lightweight E1 draft preservation still
does not require complete business setup under L-0122. Planned witnesses cover initial
absence, boundary-before/at/after, crossing the date line, midnight gap/fold, skipped date,
scheduled-chain changes and replay with retained boundaries.

## Consolidated adoption — accepted 2026-10-26

The user explicitly approved the completed consolidated planning package. The reviewed
choices and bounds in this contract are adopted under [the acceptance decision](../decisions/0171-work-calendar-precision-and-retention.md).
Earlier candidate/pending-review wording is historical and superseded for these choices.
Actual implementation and provider/database/browser/recovery proof remain delivery work.
The user requires a new Codex session before implementation; no runtime action here.
