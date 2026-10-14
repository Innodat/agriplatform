# ENV/scaffold adversary gate — 2026-10-14

Verdict: guarded disposable environment and provider/device boundaries are sound as planning requirements. Two generator ownership/input divergences need resolution before the recipe is executable. Exact versions are selected; compatibility and binaries remain delivery proof.

Reviewed `platform/docs/architecture/contracts/scaffold-environment-and-generation.md`, `scaffold-dependency-baseline-2026-10-14.md`, `kdg-shared-readiness.md` and the current KDG architecture spine. This is an independent consistency attack, not code or runtime verification.

## H1 — Recipe cannot deterministically select every claimed configuration

The recipe has exact keys/types and pattern IDs, but fixed-org versus selected-org, saving and history choices live only in referenced prose contracts. The catalogue examples distinguish organization-account from organization-person, not fixed versus selectable organization or saving/history selection. “Shell navigation/config derives only from the selected contract and explicit template support” leaves the derivation interface undefined.

Independent generator A hardcodes account-based applications to fixed organization and generates explicit-save forms for the KDG references. Generator B treats the same account pattern as selected organization and requires an organization selector, interpreting the referenced sources differently. Both can consume the same validated recipe and claim contract-derived behavior. More generally, an arbitrary existing Markdown contract path does not supply a machine-readable selection.

Disposition: select a minimal closed machine-readable configuration boundary. Existing `patterns` can carry explicit supported variant IDs for fixed/selected organization and supported saving/history behavior; alternatively declare one validated contract-profile reference whose versioned machine-readable form contains those choices. Do not duplicate domain DB/API rules or make the generator infer intent from arbitrary prose. Prove KDG fixed-org/account-own and Leave selected-org/own-person independently, plus incompatible/absent-choice refusal. This is a scaffold engineering call under ADR-0059, not new product requirements.

## H2 — Decide generated versus code-owned model/client paths after Build

The contract says source templates remain authority and generated output edits are forbidden, but also says owner models/OpenAPI become code authority after Build. `.generated-files.json` hashes generated files and regeneration refuses edits. Extensions are nonoverlapping custom module directories. It does not identify which initial skeleton files become code-owned or how they leave generated ownership.

Independent generator A hashes its generated model/route skeletons permanently; necessary first-consumer domain changes become forbidden edits and later regeneration fails. Generator B silently drops changed model files from its manifest because they are now “code authority”; later regeneration may overwrite or cease tracking them. Neither follows a declared ownership transition.

Disposition: explicitly separate immutable generator-owned artifacts from initial scaffold seeds that are code-owned from creation, or define a narrow recorded ownership transfer before editing a seed. Domain models/routes/OpenAPI authority must have one clear status. Generated clients remain generated from the owner OpenAPI with their own generator provenance. Add first-consumer edit plus regeneration preservation fixtures; no permission to hand-edit generated-warning files is introduced.

## M1 — Refresh the spine/addendum's open-input statements

The new ENV contract selects direct versions, generator command/argument boundaries and target origins/ports. The spine still says package pins/recipe/commands are open and its stack section ends with optional adapter selection without pointing to the exact new baseline. The shared addendum still lists exact tool/package/bootstrap/device target as readiness inputs without distinguishing selected input from execution qualification.

Independent implementer A follows the new selected baseline, including TS7.0.2. Implementer B follows the spine's older “open” wording and treats PtS's compatible older stack as selectable. The reuse paragraph correctly says those older ranges are not selected KDG dependencies, but it does not establish the new authority.

Disposition: link the new ENV/dependency contract as authority and split selected versions/commands/targets from unresolved compatibility, executable implementation and physical qualification. Keep the PtS package evidence clearly historical. No current application locks change during planning.

## Delivery acceptance clarifications

- Regeneration must preserve one complete prior output on interrupted replacement, including manifest and custom modules. A staged complete diff is necessary but does not by itself establish atomic replacement of a nonempty directory. The implementation can choose a filesystem strategy; acceptance must interrupt before/during replacement and inject write failure, verifying that no mixed generator manifest/tree becomes the apparent completed result. Protect concurrent custom edits with an output lock or equivalent validation at commit, rather than trusting only early preflight hashes.
- Target reset/stop protections already prohibit foreign/production identities. Delivery fixtures should exercise stale run metadata, forged project labels, a changed secret reference and a symlink substituted after preflight, including partial reset failure. Textual “localhost” or a container label alone cannot establish run ownership. Credentials need protected source/environment provenance; their bytes cannot reliably identify whether they are production credentials.
- The direct dependency record expressly leaves native-wheel/source-build, exact container identities and full resolution open. A newest stable label is not clean-install acceptance. Required peers must be finalized before claiming an exact usable baseline; the Testing Library DOM peer is explicitly pending in the reviewed text. Preserve the user's TS7.0.2 selection and qualify any TS6 compiler-API adapter only in its requiring tool owner.

## Closed attacks / no finding

- No default target or root Supabase reset exists; commands require explicit target/run and reset confirmation. Occupied fixed ports fail rather than attach to another app. Simultaneous runs therefore need separate qualified port input or refusal, not opportunistic reuse.
- Supabase's selected container set is qualified against deployment PostgreSQL; newest package preferences do not authorize a live database upgrade.
- Device aliases, LAN routing, CA trust and Entra callback qualification are explicitly assumptions, not runtime evidence. Synthetic password tests cannot substitute for genuine Entra callback acceptance. Rejected `.test` targets require a separately qualified nonproduction replacement, with no production fallback.
- The candidate-pattern proof exception is confined to the disposable internal generation harness. A normal app cannot bypass registered proof with a candidate flag.
- Owner-specific Python locks, a single frontend root lock, isolated installation without hidden repository node_modules and SERVICE's HTTP-only ownership are explicit.

Planning only. No commands, schema, dependencies, images, credentials, provider configuration or application code were changed by this review.

## Resolution recheck — 2026-10-14

Verdict: H1, H2 and M1 are resolved in the amended planning baseline. No remaining blocker from this review.

- H1: exact account.fixed/person.selected/service-owner IDs now fix auth/navigation choices. Initial saving.none/history.creation-attribution choices are explicit; later consuming patterns require exact mutually exclusive IDs. Contract prose is expressly not a selection parser.
- H2: generated adapters/clients and create-once code-owned model/route/domain seeds have explicit classifications. Regeneration preserves owner seeds and imported extension destinations; reviewed ownership conversion is required before changing classification.
- M1: the spine and shared addendum now link the exact dependency and ENV command/recipe selections, leaving execution qualification and physical owner decisions as gates.

The journal/serial-generation contract also replaces the unsupported multi-file atomicity implication: incomplete installs are recorded and recovered before generation/build proceeds. Existing documentation/custom files are preserved, and extension source/destination imports are bounded and copy-once. Real interrupted-install, concurrent-edit, restricted-target and provider/device proof still belongs to the stated delivery acceptance; this recheck does not claim implementation evidence.
