# ADR-0023: Structured Operational Logs and Sensitive Data

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** All applications and shared platform services

## Decision

Use structured operational logs to diagnose actions, failures and retries. Include
service/action identity, outcome, duration and a useful error category. Preserve the
operation identifier and downstream event/trace links under ADR-0012 where applicable.
Include internal NGO and record identifiers only where needed for investigation;
identifiers are not authorization and are not assumed anonymous.

Exclude employee notes, medical documents and other sensitive business content,
passwords, access/refresh tokens, session cookies, credentials, full signed URLs and
full request/response payloads from operational logs. Prefer explicitly selected
safe fields over dumping objects and then attempting to redact them. Apply this to
API, worker, shared-service, browser telemetry and infrastructure logging paths,
including exception handling. Scrub query strings, headers, database parameters and
third-party error text rather than allowing them to bypass this rule. Safe stack
traces may assist diagnosis; captured local variables or echoed payloads must not
leak protected data. A debug setting does not authorize sensitive payload logging.

Authorized business audit history remains the place for domain explanations and
actor/reason records, subject to existing scope and sensitive-data permissions.
Operational logs do not replace audit history or immutable decision evidence.
Restrict operational-log access to authorized operational roles and define retention
in the owning operations plan before release; this decision sets no numerical period.

User-facing errors remain plain-language and actionable. Show a non-secret operation
or diagnostic reference in expandable support details only where useful. Do not
expose stack traces, database errors, credentials or sensitive log contents in the UI.
A support reference never grants access to an operation or its records.

Example: an approval log records a coordination timeout and links the later retry
through its operation identifier, without including the employee's medical reason.

## Impact and verification

- Acceptance: correlate action/retry/downstream events; inject representative sensitive
  values into success/error paths and verify they do not appear in logs/telemetry;
  ensure support details disclose only safe references and enforce log access scope.
- Scaffold: prove and promote safe structured logging/context and error-handling
  defaults, including API/worker configuration; generation is not implemented here.
- Shared UI: reuse error/disclosure primitives; no new support screen or mandatory
  diagnostic field on ordinary business screens.
- Agent context: record the platform-wide privacy boundary in repository instructions.
- Documentation: shared experience/scaffold guidance and Leave requirements/tracker link here.
- ADR: complements 0005 and 0012; accepted predecessors unchanged.
- Planning only; no logger, telemetry provider or runtime configuration changed.
