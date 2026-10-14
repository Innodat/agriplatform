# ENV and scaffold architecture rubric review

2026-10-14. Independent bmad-architecture reviewer-gate rubric walker.

**Verdict: PASS with one medium clarification before final handoff.** The selected
ENV/scaffold baseline fixes the main independent-builder divergence points without
claiming installed tooling. This is architecture acceptance, not runtime proof or
implementation approval.

## Reviewed scope

- `platform/docs/architecture/contracts/scaffold-environment-and-generation.md`
- `platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md`
- Current KDG architecture spine and shared-readiness addendum.

The user chose newest stable direct versions and explicitly deferred affected PtS
stability qualification to delivery. This review assesses consistency and gate
meaning; exact publisher metadata/native binary fit belongs to the technology lens.
No installs, implementation, manifest/lock updates or target provisioning occurred.

## Rubric assessment

| Dimension | Assessment |
| --- | --- |
| Version authority | PASS. Exact direct versions are selected independently of existing PtS ranges. Transitive locks, native wheel/source-build qualification and affected PtS/shared regressions remain delivery evidence. Existing libraries do not silently cap the owner's selected foundation. |
| Environment isolation | PASS. Explicit target/run identity, per-run project/volume identities, fixed noncolliding ports, run metadata and target/hash guards prevent accidental attachment/reset of an existing stack. Production is excluded from the disposable command. |
| Authentication/device target | PASS as a qualified planning selection. Desktop synthetic password proof and actual Entra/device proof are distinguished. LAN DNS, trusted CA and exact provider callbacks are declared assumptions; refusal requires recorded replacement/qualification rather than production fallback. |
| Migration/setup boundaries | PASS. prepare/up/verify/stop/reset separate effects; API/project startup does not execute repository-owned migrations. Controlled owner migration/fixture commands retain authority, and local setup receipts do not imply effective consumer access. |
| Recipe scope | PASS. A bounded versioned recipe references authority/patterns rather than duplicating domain schemas or grants. Fixed-account and selected-person consumers are explicit; no mandatory People, Content, selector, draft or worker requirement is introduced. |
| Generation proof | PASS. Normal generation admits proven catalogue entries; an internal disposable harness proves candidates without a public bypass. Declared shared workspace packaging avoids a hidden dependency on existing node_modules. |
| Extension/regeneration | PARTIAL: edits/overlap guards and custom preservation are sound, but the source-to-output extension mapping needs one explicit rule (E1 below). |
| Ownership and gates | PASS. ENV/P1/SERVICE retain existing work ownership. Planned schemas/manifests/commands are explicitly absent; real locks/images/provider/device results are not claimed. Identity/Access/WRITE physical/operator/secret gates remain separate. |

## Findings

### E1 — Define extension source-to-output behavior

**Severity:** Medium. **Disposition:** Clear planning clarification before final handoff.

The recipe defines extensions as repository-relative custom module directories, while
generation promises isolated output and regeneration promises unchanged custom files.
It does not explicitly say whether an extension is copied into the output, referenced
in place, or reserved as an output directory, nor its output destination. Independent
generator/test builders could choose incompatible layouts; a source reference could
also undermine the clean disposable-install claim.

Keep the recipe thin: choose one deterministic mapping rule for extension sources to
output directories, define when their initial files are copied and which output copies
remain owner-managed, and reject ambiguous/colliding mappings. Alternatively state
that extensions are reserved owner-managed output paths and not external module inputs.
Do not add a domain runtime/plugin framework. Prove the selected rule with a disposable
extension fixture and regeneration preserving its changed custom files.

### E2 — Reconcile old open-input wording with the newly selected ENV authority

**Severity:** Low. **Disposition:** Autofix/document reconciliation.

At review time, the shared-readiness addendum still says exact pins, generation options,
bootstrap invocation and callback/device target are readiness inputs; the spine lists
pins/recipe/commands as open pre-Build decisions. The new ENV contract selects their
planning boundaries. Link that authority and distinguish selected baseline from later
compatibility/provider/executable proof so the readiness rerun does not repeatedly
reopen settled inputs or mistakenly close their delivery acceptance.

### E3 — Finish required peer selection before declaring the direct baseline final

**Severity:** Low. **Disposition:** Technology-lens completion, not an install request.

The exact-pin record says required Testing Library DOM peers are checked separately
before finalizing. Retain that explicit qualification until the required direct peer
is selected or its documented dependency ownership is established. Optional peers
need not become speculative dependencies. The technology reviewer should reconcile
this statement before final readiness reporting.

## Remaining evidence

ENV/P1 delivery still proves actual target guards, image/database compatibility,
native binaries/locks, generation/regeneration, isolated installation, real callback
and installed Android/iPhone behavior. Nothing in this review calls for implementing
them during planning or waiting for all Leave planning. Physical shared owner schemas,
privileges/operator trust and HMAC secret wiring remain independently scoped gates.

## Resolution recheck — 2026-10-14

**Final resolution verdict: PASS.** Rechecked the addressed findings only against
the updated working-tree contracts and spine. All three findings are closed for
the planning baseline; executable acceptance remains separate.

- **E1 closed:** extensions now have exact source/destination records, with a
  repository-relative source and output-relative destination. Initial import copies
  source files; later regeneration preserves app-owned destination edits. Disposable
  packaging includes those destinations/dependencies rather than external app paths.
  Escape/symlink and generated/seed/extension overlap checks close the layout seam.
- **E2 closed:** the app spine and shared addendum link the new ENV/scaffold authority
  and selected dependency baseline; exact selections are distinguished from later
  locks, installation, executable and provider/device qualification.
- **E3 closed:** the exact baseline includes Testing Library DOM 10.4.2 and explicitly
  distinguishes required peers from omitted optional compiler/Babel/canvas peers.
  Native wheel metadata is identified as metadata, with exact platform/image/hash
  qualification still assigned to delivery.

Associated adversary fixes strengthen the same boundaries: generated files and
create-once owner seeds have separate regeneration ownership, navigation/saving/history
choices use literal supported patterns rather than prose parsing, and installation
uses serialized journal/recovery instead of claiming atomic multi-file replacement.
These changes do not authorize implementation or claim an installed target.
