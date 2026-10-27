### Successful reference organization discovery is unverified

- **Changed surface:** `services/access/discovery.py:45` permits the reference caller to discover organizations for its own application; `services/access/discovery.py:49` enforces that selector.
- **Impacted consumer or site:** `GET /v2/organizations?application=reference` with the reference service credential, registered at `services/access/discovery.py:80`.
- **Existing test evidence:** `Regression gap`: `services/access/tests/test_discovery.py:70` tests reference only with the wrong selector and expects 403. Successful organization tests use Leave (`services/access/tests/test_discovery.py:36`). I searched discovery symbols and references across the repository and examined the retained native fixture builder; its organization success requests likewise use Leave (`.local/leave-discovery-20261027/qualified-v3/native_discovery_fixture.py:47`).
- **Missing verification:** A successful reference request asserting the exact reference-eligible organizations, with eligibility differing from Leave.
- **Demonstration:** Removing `reference` from the permitted organization callers at `services/access/discovery.py:45` would reject every legitimate reference request. The inspected tests would retain their expected results because their reference requests already expect denial; native success cases exercise Leave.
- **Consequence:** Reference organization discovery could ship permanently denied while the checked verification remains satisfied.
- **Disposition:** `patch` — add `test_reference_organizations_are_current_and_app_specific` and a native reference success oracle with distinct Leave/reference eligibility.
