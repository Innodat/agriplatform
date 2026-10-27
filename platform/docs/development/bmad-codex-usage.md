# BMAD Codex model-selection trial

Applies to `bmad-build` and `bmad-build-auto` through `_bmad/custom/` overrides.
BMAD remains the delivery workflow. There are no custom runtime checks or Codex hooks.

## Model selection

Use **Sol High** for the coordinator when starting a session and the client supports
that selection. Instructions do not switch an existing coordinator's model.

For delegated implementation, set both model and effort explicitly:

| Task | Model | Effort |
| --- | --- | --- |
| Default, uncertain, consequential or cross-service work | `gpt-6.1-sol` | `high` |
| Bounded exploration, summaries of supplied evidence, small fixes with clear tests | `gpt-6.1-terra` | `medium` |

Use Terra only when the scope, inputs and verification are clear. Authorization,
migrations, concurrency, service contracts and release/recovery use Sol High. Do not
split a coherent risky task into cheaper fragments to qualify. Avoid delegation for
tiny tasks where the handoff would cost more than doing the work inline.

The installed oneshot route implements inline on the coordinator; the implementation
handoff override applies to dispatch. All review agents retain the coordinator's
capability under existing BMAD rules. Bounded exploration may use Terra separately.
If the selected model is unavailable, disclose it and use an available stronger
configuration or stop; never silently downgrade or claim the requested model ran.

## Verification and session boundaries

Keep existing ATDD, focused tests, owner/native proofs and review triage. Read actual
verification results; agent reports and agreement alone are not proof. Reviewers may
return no supported findings. Recheck affected evidence after repairs. If repairs stop
making progress, reassess scope/inputs and use Sol before spending more attempts;
retain BMAD's existing loop limits and human decision gates.

At a story/phase boundary, before a large next step, or after compaction, choose
continue, compact or a fresh session. Do not stop healthy work just to ask permission
for routine context management. Before switching, record the task/next step, decision
references, unresolved findings, changed-file ownership, verification and fixture state
in the existing spec/checkpoint. Recheck current source on resumption. Use observed
headroom if available; otherwise mark it unknown. A fork inherits history. There is no
automatic session launcher or universal percentage threshold.

## Observe without extra machinery

Add one short line to the existing delivery record: selected model/effort, actual model
if exposed, retries, available usage and elapsed time. Separate model work from
test/build/provider waits when measured; unavailable values stay unknown. Do not log
credentials, business payloads or transcripts. Keep successful checks quiet and full
test logs out of model context. Evaluate total usage per accepted story and missed
defects after several stories; no separate telemetry service or mandatory reporting turn.

These settings affect newly rendered workflows. Existing snapshots do not hot-reload
overrides. Revert the two team override files to end the trial; generated defaults
remain untouched. Deferred helper work is outside the rollout.
