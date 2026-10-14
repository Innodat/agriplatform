# Shared readiness adversary gate — 2026-10-14

Verdict: the selected ownership, capability, operator and fingerprint boundaries are coherent. Two small executable-contract ambiguities should be closed before treating the selected shape as convergent. Neither requires reopening KDG requirements or implementing code. Executable privileges, secret wiring and generator proof remain correctly gated.

Reviewed `ARCHITECTURE-SPINE.md`, `platform/docs/architecture/contracts/kdg-shared-readiness.md`, the KDG section in `operation-fingerprint-security-evolution.md`, and the referenced canonical Access/admission contracts and KDG technical contracts. The sole owner's explicit acknowledgement satisfies the ownership handoff; a second external owner approval is not needed.

## Findings

### M1 — Define the clock boundary for bounded assignment execution

The shared target contract says local execution starts within one second of the observation, alongside a three-second HTTP timeout and ten-second total deadline. It supplies Access's UTC `checked_at`, but does not define whether the one-second test uses that remote clock or locally measured response age, nor when the total execution budget starts.

Independent implementation A subtracts `checked_at` from the KDG wall clock. Implementation B uses a monotonic timer after receipt. Both can claim compliance, but clock skew can make A reject fresh evidence or admit stale evidence while B behaves differently. Likewise a recheck could restart A's total budget while B preserves it. This matters to the bounded-current-authority claim, even though later creates reject retired memberships.

Suggested disposition: specify one executing attempt's monotonic total budget, beginning before its first authorization/target call; never reset it on an internal recheck. Define the observation-to-local-start bound in local monotonic terms with the HTTP round trip included or explicitly accounted for. Keep `checked_at` as UTC audit evidence, not an assumed synchronized-clock freshness calculation. A new/restarted attempt obtains fresh checks. Add delayed-response, clock-skew and internal-recheck deadline fixtures. Use the same convention for KDG's general current-check timing paragraph.

### M2 — State the point-check target predicate independently of listing

The target paragraph explicitly assigns active profile/account/membership/actor, effective create permission and current admission checks to **List**. The point-check paragraph explicitly binds the membership and returns permissions, but does not expressly say it repeats every target eligibility predicate. The setup paragraph's “same point-check model/policy” establishes setup/runtime equivalence, not unmistakably list/check target equivalence.

Independent implementation A reuses the list target predicate for point checks. Implementation B checks supplied membership and effective create grants but interprets actor/profile/app-admission filtering as listing-only behavior. Both can return the selected response shape; B could provision an assignment for a suspended target. Subsequent create authorization still prevents execution, so this is contract convergence and misleading setup evidence rather than an immediate authorization bypass.

Suggested disposition: expressly require point-check and list to apply the same current target account/profile, membership, durable account actor, global/org admission and effective create predicate. Clarify that setup replaces only acting-user authorization with protected executor/operator authorization. Preserve declared 404 concealment and 503 dependency failure; add list/check/setup parity fixtures for target disable, missing actor and membership replacement. Display-name formatting remains a list presentation condition rather than an accidental assignment identifier.

### L1 — Give wrong-environment key fixture a concrete acceptance outcome

The fingerprint contract correctly selects separate environment-owned secrets and lists a wrong-environment-key fixture. The physical secret paths and permissions are explicitly deferred ENV inputs. The fixture does not yet specify how a wrong environment configuration is identified: a valid 32-byte key and opaque key ID alone contain no environment identity.

Independent deployment A verifies the secret reference against a protected environment-bound deployment manifest before activation. Deployment B only validates key length/ID and relies on correct secret mounting. The latter may start successfully with another environment's valid key; a later existing-outcome retry becomes a misleading payload mismatch.

Suggested disposition: keep this as the existing ENV delivery gate, but require protected environment/key-reference binding evidence and activation refusal for a deliberate wrong-environment fixture. No new key service or cryptographic envelope is necessary. Do not promise that an arbitrary secret byte substitution can be diagnosed solely from an HMAC mismatch.

## Attacks that the baseline already closes

- Organization authorization cannot fall back to account authority; all nine KDG literals have organization scope, and own-account versus all-organization resource shapes are fixed by literal. Create-all still creates only the caller's records. No person/employment dependency is introduced.
- `session_user` identifies the authenticated database login before `SET ROLE`; payload/current-user/session-setting spoofing cannot select an operator actor. Exact real privileges and bootstrap mapping remain ID-B prerequisites, not assumed implementation evidence.
- Runtime bearer/service identity cannot become setup authority. Setup verification permits no target enumeration, grant write or target impersonation, and each owner keeps its own writer credentials.
- Membership replacement requires explicit renewal. Old account-owned records may remain accessible through newly approved read/edit rights without reviving old create eligibility.
- Rotation preserves stored key identity and retained verification keys, including overlapping releases and ordinary rollback. Missing referenced keys produce unavailable verification rather than unknown outcomes or fresh execution. Authorized receipt lookup is deliberately distinct from payload replay.
- Database-only HMAC protection does not claim encryption, runtime-compromise protection or retroactive confidentiality after key compromise. Sensitive canonical content and fingerprint material are excluded from diagnostic output.

No critical or high finding established. Apply M1/M2 as contract clarifications during planning; carry L1 into the existing ENV evidence gate. Retain all stated pre-Build and pre-pilot gates.
