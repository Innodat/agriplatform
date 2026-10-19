# Pinned Kong image Config authority

Public API 1.48 Config projection independently observed read-only from
`GET /v1.48/images/sha256:3cefb958bcd694597b65adc00053a762b1f9a6df3c6031af528d052d75a64e1a/json`.
The image reported Linux/amd64. The selected Kong 2.8.1 reference is resolved from
existing owner-qualified pinned selection, never from an ambient tag.

`supabase-kong-image-api-config.json` retains exactly that public projection;
its SHA256 is `33f41b2a864c66de040bd8ad42dc637cb6565cfe251439b1acfadad9616c45a4`.
The root observation is retained under
`platform/deployment/.local/kong-execution-profile/pinned-image-api-config.json`
and `image-observation.json`. These private evidence files are not fixture inputs.
Both public fixture files participate in existing source custody via `dev.SOURCES`.

The validator compares every Config key/type/value and refuses unknown defaults,
including Env, labels, volumes, healthcheck, entrypoint and shell. Before boundary
classification the selected reference is inspected through the existing session;
its current Id/platform must match the existing owner-qualified selection.

The disposable request explicitly retains all three image Env defaults and the
maintainer label, unions the image/source exposed TCP ports (8000/8001/8088/8443/8444),
and overrides entrypoint/command, user, workdir, healthcheck and stop signal. Docker
is expected to merge matching explicit defaults idempotently and preserve explicit
source values. This is a documented merge expectation, not observed container merge
conformance. The source request, script, synthetic markers and three transfer files
remain independent. Both create requests are classifier-only refusals. No Kong
create/copy/start, routing proof, native token, readiness or fresh setup is claimed.
