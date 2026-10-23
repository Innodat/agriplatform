# KDG questionnaire definition prerequisite

bmad-help [BD] selected the small app-owned definition contract before Story1.2's
published-version persistence/read work. Full Story1.2 remains gated by its owner-write,
operator/release evidence and fingerprint-based bootstrap contract; fingerprints/HMAC
remain deferred. This delivery neither bypasses those gates nor changes their design.

The owner model uses approved Pydantic2.14.1 discriminated unions and standard JSON.
It validates version1, ordered1–50 unique canonical question IDs, strict booleans/scale,
closed rating/boolean/text fields and bounded nonblank Unicode labels. The safe bounded
JSON parser rejects duplicate keys, malformed/nonfinite data and invalid content with
one fixed identifier, suppressing raw input and chained diagnostic rendering.

The initial factory takes exactly four explicit IDs and returns the four approved
Afrikaans labels, required flags,1–5 endpoint meanings, default-Nee booleans and optional
Ja-only Besonderhede configuration. It allocates no IDs and performs no I/O. Model
immutability is distinct from published database immutability and actual form behavior.

Behavioral ATDD RED: duplicate question IDs were accepted by the initial model skeleton,
so the expected DefinitionError was not raised. The implementation fixes it. Focused
TDD subsequently exposed byte-ID coercion and a missing false constant in generated
JSON Schema; both failed before the strict-ID/default corrections. An initial uppercase
fixture contained only digits and was corrected to contain uppercase hex, rather than
changing an expected result to suppress a domain failure.56 focused cases pass.

The actual HTTP OpenAPI export stays unchanged and the existing TypeScript7.0.2 contract
check passes. No route/client type is invented for an unused domain candidate. The
first API consumer must reuse this model. Broader API regression uses synthetic HTTP
transports; no real Auth, database, Docker lifecycle, account/access or provisioning
occurs. The in-sandbox regression stalled and was interrupted; the bounded rerun outside
the restricted process sandbox supplies the final result in the receipt.

Independent build review of model/test/spec finds no confirmed issue. Scaffold impact:
questionnaire semantics/content remain KDG-owned; no generic form engine or speculative
helper/test promotion. Shared UI unchanged. Existing agent context sufficient. Owner
contract/guide/testing/handoff updated. Accepted ADRs unchanged. Historical native schema
proof/resources, concurrent work and approved dependencies/locks remain preserved.

This is not Story1.2 completion, a published version, answer validation, persistence,
operator/replay implementation, read endpoint, editor, release or production readiness.
No Leave/editor, real accounts/access, production, general provisioning, deployment/pilot,
cleanup or fingerprint/HMAC work. Exact commands/results, source/log bindings and remaining
limits are in the [receipt](evidence/questionnaire-definition-20261023.json).
