# KDG architecture decisions

Application decisions link platform decisions. Accepted records are immutable;
proposed records may be revised through planning.

| ADR | Status | Decision |
| --- | --- | --- |
| [0001](0001-explicit-observation-save.md) | Proposed | Explicit observation Save without unfinished-entry recovery |
| [Platform 0061](../../../../../platform/docs/architecture/decisions/0061-kdg-first-committed-operation-wins.md) | Accepted | KDG capture.create/edit first committed request wins; partially supersedes platform ADR-0012 changed-content rejection, defers fingerprints/HMAC/key lifecycle |
