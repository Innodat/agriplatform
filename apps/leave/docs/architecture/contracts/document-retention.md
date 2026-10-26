# Leave document retention

**Status:** Candidate applicability details for the consolidated planning review,
2026-10-25. No configuration, deletion or legal determination has occurred.
**Owners:** Leave 4.10 settings; 4.11-L domain release; Content 4.11-S physical disposal.
**Authority:** Features §12, Leave ADR-0006, platform ADR-0025/0030/0033/0051/0054 and
[Content association/reclamation](../../../../../platform/docs/architecture/contracts/content-association-and-reclamation.md).

## Default, precedence and applicability

Retain the accepted medical-document default of two calendar years after request closure.
The initial field is a positive whole number of calendar months (default 24; supported
1–1200); the form can present years/months but persists one duration. No immediate-delete,
indefinite-draft-expiry or legal-hold control is added. A configured duration is an
organization's reviewed instruction, not an assertion that Leave determines the law.
Production adoption still needs that organization's legal/privacy review.

Use a versioned organization default and optional explicit jurisdiction overrides. The
jurisdiction-specific reviewed value takes precedence over the organization default,
which takes precedence over the initial 24-month medical default. A document supporting
multiple applicable jurisdictions uses the longest applicable reviewed duration; do not
pick the currently selected UI location or infer applicability from an employee's current
address. Bind applicability to the request's retained work/jurisdiction history for its
requested dates. Unknown or conflicting required source data blocks automatic disposal
and appears in restricted operational reconciliation, without blocking ordinary draft saving.

A settings Save applies to request closures occurring after that settings version becomes
effective. Already-closed request attachments retain their recorded duration and deadline;
a shorter new setting does not silently shorten existing deadlines. The pre-Save impact
projection explicitly states this and counts affected future/open versus already-closed
records without disclosing filenames/content. This prospective model is a candidate
refinement of the accepted configurable retention scope, not a claim that retrospective
shortening was already approved. A later exceptional legal correction needs explicit
owning design/evidence rather than an undocumented background reinterpretation.

## Closure and reopening

A draft has no request-closure retention clock. A rejected/withdrawn/cancelled request
closes at its durable terminal transition once no active response/decision step remains.
An approved request closes after its last recorded requested civil date ends in the
request's retained work-timezone basis and all local completion effects resolve. Future
approved leave is not already closed merely because approval finished. Closure is a
recorded domain event with lifecycle generation, timestamp and rule basis, not a worker's
last-run timestamp. If past import data lacks verified closure evidence, do not fabricate
an import-time closure for automatic deletion; reconcile it through E8.

Where the accepted workflow permits reopening/resubmission, the owner atomically removes
current disposal eligibility and protects the association before reopening can commit.
A later genuine closure records a new closure generation and its applicable setting;
original closure evidence remains immutable. An already-disposed file cannot be revived:
the workflow must truthfully require replacement where needed. Reopening and Content's
disposal fence cannot both win on the same association. E5/E6 implement and prove those
actual consumers before their activation; E4 uses exact owner lifecycle fixtures.

Calculate calendar-month anniversaries in the retained closure timezone, clamping an
absent day to that month's final day; e.g. 29 February plus 24 months becomes 28 February.
Persist the resulting UTC deadline and its closure/timezone/settings version evidence.
Do not recalculate it from today's timezone or a changed calendar library without a
versioned migration and compatibility proof. This is retention timing, separate from
ADR-0168's cancellation cutoff and the accounting effective date.

## Save and disposal

The existing organization Leave settings Documents → Retention form uses whole-form
Save/Cancel under explicit Leave configuration capability. Read/manage settings grants
no medical-document read. Input failure preserves useful input; conflict/uncertain Save
resolves the existing revision/operation contract. Save commits configuration/version/
attribution/history together and never deletes bytes.

4.11-L computes eligibility from recorded closure/deadline, current lifecycle generation
and legitimate references, then commits local release and outbound intent. Content still
checks its independent reference/disposal fence. Settings review does not reserve a
future deletion or override pending/saved protection. Release, physical provider deletion
and eventual backup expiry have distinct observable outcomes. Retain minimum permitted
disposition evidence; request/approval history remains.

## Acceptance and impacts

4.10 proves default/organization/jurisdiction precedence; multiple-jurisdiction maximum;
positive bounded duration validation; exact before-Save applicability; already-closed
retention after shortening; explicit Save/Cancel; conflict/replay; configuration-only
permission and zero deletion on Save. 4.11-L proves unknown/imported closure, no draft
expiry, future approved requests, leap-day/month-end examples, closure/reopen/disposal
races, account/resource denial and truthful post-disposal metadata. Content proves the
physical fence/provider/recovery side once through 4.11-S.

Scaffold/shared UI: reuse explicit-Save, typed impact/revision/outcome and date fixtures;
Leave owns legal applicability and lifecycle. Agent context: existing owner/privacy and
saving rules suffice. Documentation: source/criterion mapping, settings applicability,
release/recovery evidence and operational unresolved-item handling. Existing accepted
ADRs remain immutable. Any material change after consolidated review must update the
owning product/UX source before the affected implementation story is declared ready.

## Consolidated adoption — accepted 2026-10-26

The user explicitly approved the completed consolidated planning package. The reviewed
choices and bounds in this contract are adopted under [the acceptance decision](../decisions/0171-work-calendar-precision-and-retention.md).
Earlier candidate/pending-review wording is historical and superseded for these choices.
Actual implementation and provider/database/browser/recovery proof remain delivery work.
The user requires a new Codex session before implementation; no runtime action here.
