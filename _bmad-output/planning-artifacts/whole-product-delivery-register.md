# Whole-product delivery and size register

**Adopted 2026-10-26:** Explicit user approval resolves the final candidate-review gate.
The approved choices are recorded in platform ADR-0064 and Leave ADR-0171. Earlier
pending-approval wording is historical; source/criterion bodies and dependencies unchanged.
Implementation is held for a new Codex session at the user's request.

**Final delta — 2026-10-26:** Invitation, administration continuity and calendar/precision
inputs are now bound as candidates in [final reconciliation](final-contract-reconciliation.md).
Existing criterion bodies and dependency graph remain unchanged; the single consolidated
review is ready. Earlier remaining-contract/G01 notes below are superseded.

**Date:** 2026-10-25. **Status:** Validation candidate, not a readiness PASS.
Use the [validation result](whole-product-validation.md) for limitations and findings.
Source stories/ACs remain in epics; this register is traceability, not a duplicate spec.

There are 307 current planning entries: E1 24, E2 26, E3 48, E4 14 source scopes,
E5 88, E6 46, E7 31 and E8 30. E4's accepted shared/Leave allocation yields 17
owner graph candidates instead of 14 undifferentiated scope records, for 310 graph
nodes. Six child stories now bind those partitions to exact parent clauses and the owning race protocol; provider feasibility remains G03.
Parent E1 ID/ACCESS/D2, seven E3 parents, absorbed 3.40 and E5 source parents are
not additional executable work. No new feature or measured one-sitting estimate.

All nodes are source-backed and every edge has an existing scope. Layers are a
mechanical dependency view, not an instruction to run agents, serialize unrelated
work, or permission to activate anything. E5 internal edges are preserved; external
edges bind actual earlier owner outputs, not service-file existence as completion.

| Node | Actual owner / bounded outcome | Predecessors | Size status |
| --- | --- | --- | --- |
| E1-ENV | Platform environment: Reproduce an isolated development and acceptance environment | None | bounded-remaining-delta-assessed |
| E1-P1 | Platform builder: Generate a runnable application foundation safely | E1-ENV | bounded-remaining-delta-assessed |
| E1-SERVICE | Platform builder: Generate an independently owned internal service | E1-P1 | bounded-remaining-delta-assessed |
| E1-ID-A | Identity: Establish a verified identity migration baseline | E1-ENV, E1-SERVICE | bounded-remaining-delta-assessed |
| E1-ID-B | Identity: Link accounts to people and preserve membership history | E1-ID-A | bounded-remaining-delta-assessed |
| E1-ACCESS-A | Access: Configure application admission and grants safely | E1-ID-B, E1-SERVICE | bounded-remaining-delta-assessed |
| E1-ACCESS-B | Access: Enforce current application and user access | E1-ACCESS-A | bounded-remaining-delta-assessed |
| E1-CONTENT-READ | Content: Protect owned files and stream private reads | E1-ACCESS-B, E1-ID-B, E1-SERVICE | bounded-remaining-delta-assessed |
| E1-DISCOVERY | Access/Directory: Discover only currently accessible organizations and apps | E1-ACCESS-B | bounded-remaining-delta-assessed |
| E1-PEOPLE | People: Resolve my shared employment for the selected organization | E1-SERVICE, E1-ACCESS-B, E1-ID-B | bounded-remaining-delta-assessed |
| E1-WRITE | Platform owned-write: Prove safe owned writes for generated backends | E1-P1, E1-SERVICE, E1-ID-B, E1-ACCESS-B | bounded-remaining-delta-assessed |
| 3.22 | Notification service: Durably accept notification events | E1-SERVICE, E1-ID-B, E1-ACCESS-B | bounded-remaining-delta-assessed |
| 8.1 | Leave import/qualification: Validate a versioned consultant import package without business writes | E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.21 | Leave import/qualification: Verify recoverable backup capability across actual owners and private bytes | E1-ACCESS-B, E1-ENV | conditional-retain |
| E1-LAUNCHER | Directory/web: Show accessible apps with honest discovery states | E1-DISCOVERY | bounded-remaining-delta-assessed |
| E1-REF | Platform reference: Prove a generated authenticated application against real persistence | E1-WRITE, E1-ACCESS-B, E1-P1 | bounded-remaining-delta-assessed |
| 2.11 | People + Leave consumer: Add an employee with an initial employment period | E1-PEOPLE | bounded-remaining-delta-assessed |
| 2.14 | People + Leave consumer: Maintain simple organization departments and locations | E1-PEOPLE | bounded-remaining-delta-assessed |
| 3.25-A | Notification service: Process channel deliveries and create in-app notifications | 3.22 | bounded-remaining-delta-assessed |
| 4.1 | Content: Start or resume an authorized Content upload | E1-CONTENT-READ, E1-ACCESS-B | bounded-owner-delta-assessed |
| 8.22 | Leave import/qualification: Rehearse consistent database, document and dependency restoration | 8.21, E1-ACCESS-B, E1-ENV | conditional-retain |
| E1-A1 | Leave API/web: Sign in and enter an authorized Leave organization | E1-LAUNCHER, E1-PEOPLE | bounded-remaining-delta-assessed |
| E1-PTS-ADOPT | PtS/Access/Content consumers: Use PtS through individual platform access | E1-CONTENT-READ, E1-ACCESS-B, E1-LAUNCHER | bounded-remaining-delta-assessed |
| E1-VERIFY | Platform reference/deployment: Exercise the shared reference journey in hosted environments | E1-REF, E1-ENV | bounded-remaining-delta-assessed |
| 2.12 | People + Leave consumer: Record an employment end date with reviewed consequences | 2.11 | bounded-remaining-delta-assessed |
| 2.15 | People + Leave consumer: Assign or clear an employee's department and location | 2.11, 2.14 | bounded-remaining-delta-assessed |
| 2.16 | People + Leave consumer: Assign or clear an employee's supervisor | 2.11 | bounded-remaining-delta-assessed |
| 3.25-B | Notification service: Deliver notification emails and recover uncertain provider outcomes | 3.25-A | bounded-remaining-delta-assessed |
| 3.26 | Notification service: Read a scoped notification inbox and manage read state | 3.25-A, E1-ACCESS-B | bounded-remaining-delta-assessed |
| 4.2 | Content: Verify and finalize uploaded content | 4.1 | bounded-owner-delta-assessed |
| E1-CONTEXT | Leave API/web: Explain whether I can start or edit a Leave draft | E1-PEOPLE, E1-A1 | bounded-remaining-delta-assessed |
| 2.1 | Identity/Access + app consumer: Enable or suspend Leave for an organization | E1-ACCESS-A, E1-ACCESS-B, E1-A1 | bounded-remaining-delta-assessed |
| 2.13 | People + Leave consumer: Record a return to employment without replacing the employee | 2.12 | bounded-remaining-delta-assessed |
| 2.17 | People + Leave consumer: Replace a supervisor for selected employees | 2.16 | bounded-remaining-delta-assessed |
| 2.18 | Leave configuration: Configure an organization holiday calendar | E1-A1, E1-WRITE | bounded-remaining-delta-assessed |
| 3.27 | Leave accounting/configuration/web: Show the notification panel and organization unread indicators | 3.26, E1-A1 | bounded-remaining-delta-assessed |
| 4.3 | Content/provider: Use the organization's configured storage provider consistently | 4.2, E1-PTS-ADOPT | bounded-owner-delta-assessed |
| E1-CHOICES | Leave API/web: Choose a leave type and its permitted duration mode | E1-CONTEXT | bounded-remaining-delta-assessed |
| 2.19 | Leave configuration: Create a reusable Leave work profile | 2.18 | bounded-remaining-delta-assessed |
| 2.2 | Identity/Access + app consumer: Assign Leave roles to an existing organization member | 2.1, E1-ID-B | bounded-remaining-delta-assessed |
| 2.6 | Identity/Access + app consumer: Invite a person to join an organization securely | E1-ID-B, 2.1 | bounded-remaining-delta-assessed |
| 4.4-S | Content: Shared pending/confirmed references, identity/retry, cleanup fence and first-use read protocol | 4.2, 4.3 | bounded-owner-delta-assessed |
| E1-D1 | Leave API/web: Create or resume my application draft | E1-CHOICES, E1-WRITE | bounded-remaining-delta-assessed |
| 2.10 | Identity/Access + app consumer: Remove a member's organization access without erasing history | 2.2, E1-ID-B | bounded-remaining-delta-assessed |
| 2.20 | Leave configuration: Assign or change an employee's Leave work profile | 2.19, 2.11 | bounded-remaining-delta-assessed |
| 2.21 | Leave configuration: Set or change the organization's default Leave work profile | 2.19 | bounded-remaining-delta-assessed |
| 2.3 | Identity/Access + app consumer: Create or duplicate an application-specific custom role | 2.2 | bounded-remaining-delta-assessed |
| 2.7 | Identity/Access + app consumer: Verify a trusted Microsoft Entra tenant for an organization | 2.6 | bounded-remaining-delta-assessed |
| 2.9 | Identity/Access + app consumer: Prepare and activate application access before first sign-in | 2.2, 2.6 | bounded-remaining-delta-assessed |
| 3.1 | Leave accounting/configuration/web: Create and view an organization's leave types | E1-CHOICES, E1-WRITE | bounded-remaining-delta-assessed |
| 4.11-S | Content: Physical disposal, provider outcome/retry, reference exclusion and restricted worker/claim proof | 4.4-S, 4.3 | bounded-owner-delta-assessed |
| E1-D2-A | Leave API/web: Save and read my draft input safely | E1-D1 | bounded-remaining-delta-assessed |
| 2.22 | Leave configuration: Override an employee's work settings or restore profile inheritance | 2.20, 2.21 | bounded-remaining-delta-assessed |
| 2.25 | Leave configuration: See actionable setup status from saved configuration | E1-A1, 2.11, 2.18, 2.21, 2.2 | bounded-remaining-delta-assessed |
| 2.4 | Identity/Access + app consumer: Review and apply changes to a custom role held by members | 2.3 | bounded-remaining-delta-assessed |
| 2.5 | Identity/Access + app consumer: Delete an unassigned custom role while preserving its history | 2.3 | bounded-remaining-delta-assessed |
| 2.8 | Identity/Access + app consumer: Explicitly enable automatic onboarding from a trusted tenant | 2.7 | bounded-remaining-delta-assessed |
| 3.2 | Leave accounting/configuration/web: View a leave type's policy and version history | 3.1 | bounded-remaining-delta-assessed |
| 4.12-S | Content: Abandoned-upload discovery/reconciliation with existing reference fences | 4.4-S, 4.11-S | bounded-owner-delta-assessed |
| E1-D2-B | Leave API/web: Edit, autosave, close and reopen my draft | E1-D2-A, E1-REF | bounded-remaining-delta-assessed |
| 2.23 | Leave configuration: Review and publish changes to a shared work profile | 2.22, 2.21 | bounded-remaining-delta-assessed |
| 2.26 | Leave configuration: View an employee's employment and Leave work settings together | 2.22, 2.16, 2.15 | bounded-remaining-delta-assessed |
| 3.3-A | Leave accounting/configuration/web: Review and publish an initial policy through the API | 3.2 | bounded-remaining-delta-assessed |
| 4.14 | Content/Expense/PtS rollout: Actual old-caller inventory and replacement/retirement proof; no dependency on Leave 4.13 | 4.3, E1-PTS-ADOPT, 4.11-S, 4.12-S | bounded-owner-delta-assessed |
| 4.4-L | Leave: Actual scoped draft association, revision/limits/recovery and basic removal/release | 4.4-S, E1-D2-A | bounded-owner-delta-assessed |
| E1-D3 | Leave API/web: Switch organizations without losing or mixing draft data | E1-D2-B, E1-DISCOVERY | bounded-remaining-delta-assessed |
| E1-D4 | Leave API/web: Deliberately discard my draft and start again | E1-D2-B | bounded-remaining-delta-assessed |
| E1-D5 | Leave API/web: Return safely to my draft after sign-in expires | E1-D2-B, E1-A1 | bounded-remaining-delta-assessed |
| 2.24 | Leave configuration: Archive an unused work profile without losing its history | 2.20, 2.21, 2.23 | bounded-remaining-delta-assessed |
| 3.3-B | Leave accounting/configuration/web: Configure and publish an initial policy in the web editor | 3.3-A | bounded-remaining-delta-assessed |
| 3.5 | Leave accounting/configuration/web: Explain which policy applies to an employee | 3.3-A, 2.11 | bounded-remaining-delta-assessed |
| 3.7 | Leave accounting/configuration/web: Calculate leave duration from the employee's work schedule | 2.18, 2.22, 3.3-A | bounded-remaining-delta-assessed |
| 3.9 | Leave accounting/configuration/web: Preserve an ordered history of actual balance changes | E1-WRITE, 3.3-A, E1-ID-B | bounded-remaining-delta-assessed |
| 4.12-L | Leave: Actual saved-draft/pending confirmation protection and owner recovery evidence | 4.4-L, 4.12-S | bounded-owner-delta-assessed |
| 4.5 | Leave web: Upload supporting documents in my leave draft | 4.4-L, E1-D2-B | bounded-owner-delta-assessed |
| 5.1 | Leave request/approval/source consumer: Resolve my configured approval route and explain setup problems | 2.16, 3.3-A, E1-ACCESS-B, E1-PEOPLE, E1-WRITE | conditional-retain |
| 8.2 | Leave import/qualification: Resolve import identities and owner prerequisites explicitly | 2.26, 8.1, E1-ACCESS-B, E1-ENV, E1-ID-B, E1-PEOPLE | conditional-retain |
| 3.23 | Leave accounting/configuration/web: Save notification intent atomically with Leave changes | 3.9, 3.22 | bounded-remaining-delta-assessed |
| 3.4 | Leave accounting/configuration/web: Review starter examples before activating a policy | 3.3-B | bounded-remaining-delta-assessed |
| 3.6 | Leave accounting/configuration/web: View and select employees for a policy | 3.5, 2.26 | bounded-remaining-delta-assessed |
| 3.8 | Leave accounting/configuration/web: Calculate daily earned entitlement | 3.7, 3.3-A | bounded-remaining-delta-assessed |
| 4.6 | Leave API/web: Show document status without exposing protected details | 4.5 | bounded-owner-delta-assessed |
| 4.8 | Leave API/web: Remove or replace a document on my editable draft | 4.5, 4.4-L | bounded-owner-delta-assessed |
| 5.10-A | Leave request/approval/source consumer: Preserve request state and provide authorized current reads | 2.11, 3.9, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.2 | Leave request/approval/source consumer: Check temporary-approver eligibility and authority limits | 2.16, 3.3-A, 5.1, E1-ACCESS-B, E1-PEOPLE, E1-WRITE | conditional-retain |
| 3.10 | Leave accounting/configuration/web: Apply accumulated-balance caps to daily earning | 3.8, 3.9 | bounded-remaining-delta-assessed |
| 3.24 | Leave accounting/configuration/web: Hand over Leave notifications through a recoverable worker | 3.23 | bounded-remaining-delta-assessed |
| 4.10 | Leave settings: Configure supporting-document retention | 4.6, E1-WRITE | bounded-owner-delta-assessed |
| 4.7 | Leave file consumer: Leave browser/auth/private read integration only; shared streaming remains E1-CONTENT-READ | 4.6, E1-CONTENT-READ | bounded-owner-delta-assessed |
| 5.10-C | Leave request/approval/source consumer: Recover request operations through the existing Leave outcome API | 5.10-A, E1-ACCESS-B, E1-D2-A, E1-WRITE | conditional-retain |
| 5.4 | Leave request/approval/source consumer: Apply the configured approval fallback during absence | 2.16, 3.3-A, 5.1, 5.2, E1-ACCESS-B, E1-PEOPLE, E1-WRITE | conditional-retain |
| 7.21 | Shared owner read + Leave consumer: Read Identity/Access audit evidence through its owner | 5.10-A, E1-ACCESS-A, E1-ACCESS-B, E1-ID-B | conditional-retain |
| 7.22 | Shared owner read + Leave consumer: Read People audit evidence through its owner | 2.12, 2.16, 5.10-A, E1-ACCESS-B | conditional-retain |
| 7.24 | Shared owner read + Leave consumer: Read notification delivery audit evidence through its owner | 3.22, 3.25-B, 5.10-A, E1-ACCESS-B | conditional-retain |
| 7.25 | Leave report/read: Query existing Leave audit events with protected fields | 5.10-A, E1-ACCESS-B | conditional-retain |
| 3.11 | Leave accounting/configuration/web: Calculate upfront annual entitlement | 3.7, 3.10 | bounded-remaining-delta-assessed |
| 4.11-L | Leave: Actual closure/settings/domain eligibility and recoverable release adapter | 4.10, 4.11-S | bounded-owner-delta-assessed |
| 4.9 | Leave notification producer: Notify me when a document needs attention | 4.8, 3.24, 3.25-B | bounded-owner-delta-assessed |
| 5.3 | Leave request/approval/source consumer: Check approval coverage throughout an applicant's absence | 2.16, 3.3-A, 5.1, 5.2, 5.4, E1-ACCESS-B, E1-PEOPLE, E1-WRITE | conditional-retain |
| 7.23 | Shared owner read + Leave consumer: Read Content audit evidence through its owner | 4.11-S, 4.7, 5.10-A, E1-ACCESS-B | conditional-retain |
| 8.19 | Leave import/qualification: Prove one bounded monitoring setup with safe correlation | 3.24, E1-ACCESS-B, E1-ENV, E1-VERIFY | conditional-retain |
| 3.12 | Leave accounting/configuration/web: Calculate monthly entitlement instalments | 3.11 | bounded-remaining-delta-assessed |
| 4.13 | Leave integrated proof: Prove the complete Leave attachment journey | 4.9, 4.7, 4.11-L, 4.12-L | bounded-owner-delta-assessed |
| 5.28-C | Leave request/approval/source consumer: Expose minimum approval-coverage attention before first request use | 3.24, 3.25-B, 5.10-A, 5.3, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 7.26 | Leave report/read: Compose a chronological audit page from authorized owner evidence | 5.10-A, 7.21, 7.22, 7.23, 7.24, 7.25, E1-ACCESS-B | conditional-retain |
| 8.16 | Leave import/qualification: Verify configured retention and auditable document disposal | 4.10, 4.11-L, 4.12-L, E1-ACCESS-B, E1-ENV | conditional-retain |
| 3.13 | Leave accounting/configuration/web: Calculate monthly entitlement across partial employment and rate changes | 3.12 | bounded-remaining-delta-assessed |
| 3.14 | Leave accounting/configuration/web: Calculate carry-over at a leave-year boundary | 3.13 | bounded-remaining-delta-assessed |
| 3.15 | Leave accounting/configuration/web: Calculate entitlement expiry dates and effects | 3.14 | bounded-remaining-delta-assessed |
| 3.16 | Leave accounting/configuration/web: Calculate changes between entitlement availability methods | 3.15 | bounded-remaining-delta-assessed |
| 3.17-A | Leave accounting/configuration/web: Compose a reproducible current leave balance | 3.16, 3.9 | bounded-remaining-delta-assessed |
| 3.17-B | Leave accounting/configuration/web: Read an authorized current balance from authoritative history | 3.17-A | bounded-remaining-delta-assessed |
| 3.18 | Leave accounting/configuration/web: Project funding for every requested leave date | 3.17-B, 3.7 | bounded-remaining-delta-assessed |
| 3.19 | Leave accounting/configuration/web: Show a clear leave-request preview in Apply | 3.18, E1-D2-B | bounded-remaining-delta-assessed |
| 3.20 | Leave accounting/configuration/web: Explain request restrictions and required information in Apply | 3.19 | bounded-remaining-delta-assessed |
| 3.21 | Leave accounting/configuration/web: Calculate an exceptional funding proposal | 3.20 | bounded-remaining-delta-assessed |
| 3.41 | Leave accounting/configuration/web: Calculate request previews without an entitlement balance | 3.20, 3.18 | bounded-remaining-delta-assessed |
| 3.28 | Leave accounting/configuration/web: Review and confirm initial employee policy assignments | 3.18, 3.41, 3.24, 3.25-B, 3.6 | bounded-remaining-delta-assessed |
| 3.29 | Leave accounting/configuration/web: Review and confirm a one-off leave-balance adjustment | 3.28, 3.24, 3.25-B, 3.21 | bounded-remaining-delta-assessed |
| 5.6 | Leave request/approval/source consumer: Validate requested duration and same-date limits | 2.12, 3.18, 3.28, 3.7, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.7 | Leave request/approval/source consumer: Check employment, policy eligibility and permitted request dates | 2.12, 3.18, 3.28, 3.7, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 3.30 | Leave accounting/configuration/web: Change recurring employee entitlement or return to policy | 3.29 | bounded-remaining-delta-assessed |
| 3.31 | Leave accounting/configuration/web: Understand my leave balance and history | 3.29, 3.17-B | bounded-remaining-delta-assessed |
| 5.8-A | Leave request/approval/source consumer: Record and settle request commitments through protected owner operations | 3.18, 3.9, 5.10-A, 5.10-C, 5.6, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.9 | Leave request/approval/source consumer: Check required supporting documents before submission and final approval | 4.4-L, 4.6, 4.7, 5.6, 5.7, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 3.32 | Leave accounting/configuration/web: View an employee's Leave entitlement settings | 3.30, 2.26 | bounded-remaining-delta-assessed |
| 3.34-A | Leave accounting/configuration/web: Review and publish a used-policy change through the API | 3.30, 3.28 | bounded-remaining-delta-assessed |
| 3.42-A | Leave accounting/configuration/web: Understand untracked leave in My Leave and Apply | 3.41, 3.31 | bounded-remaining-delta-assessed |
| 5.10-B | Leave request/approval/source consumer: Finalize existing requests through current gates and atomic accounting | 3.24, 3.25-B, 5.1, 5.10-A, 5.10-C, 5.2, 5.28-C, 5.3, 5.4, 5.6, 5.7, 5.8-A, 5.9, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.19-A | Leave request/approval/source consumer: Withdraw my pending request through the protected API | 3.24, 3.25-B, 5.10-A, 5.10-C, 5.8-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 3.33 | Leave accounting/configuration/web: See policy and entitlement setup issues | 3.32, 2.25 | bounded-remaining-delta-assessed |
| 3.34-B | Leave accounting/configuration/web: Review and publish a used-policy change in the web editor | 3.34-A, 3.3-B | bounded-remaining-delta-assessed |
| 3.35-A | Leave accounting/configuration/web: Amend or cancel a scheduled policy change through the API | 3.34-A | bounded-remaining-delta-assessed |
| 3.36-A | Leave accounting/configuration/web: Review and confirm assignment changes through the API | 3.28, 3.34-A | bounded-remaining-delta-assessed |
| 3.39 | Leave accounting/configuration/web: Change an existing leave type's details and permitted units | 3.34-A, E1-CHOICES | bounded-remaining-delta-assessed |
| 3.42-B | Leave accounting/configuration/web: Explain untracked leave in employee administration | 3.32, 3.41 | bounded-remaining-delta-assessed |
| 5.18-A | Leave request/approval/source consumer: Decide an assigned request through the protected API | 3.24, 3.25-B, 5.10-A, 5.10-B, 5.10-C, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.1 | Leave correction: Project correction consequences from retained history | 3.18, 5.10-A, 5.10-B, 5.10-C | conditional-retain |
| 3.35-B | Leave accounting/configuration/web: Review scheduled policy amendments and cancellations in the web UI | 3.35-A, 3.34-B | bounded-remaining-delta-assessed |
| 3.36-B | Leave accounting/configuration/web: Review assignment changes in the focused editor | 3.36-A, 3.34-B | bounded-remaining-delta-assessed |
| 3.37 | Leave accounting/configuration/web: Deactivate a leave type while preserving its history | 3.36-A, 3.35-A, 3.29 | bounded-remaining-delta-assessed |
| 5.15-A | Leave request/approval/source consumer: Integrate one-off balance adjustments with actual pending requests | 3.24, 3.25-B, 3.29, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-C | Leave request/approval/source consumer: Integrate recurring entitlement changes with pending requests | 3.24, 3.25-B, 3.30, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-E | Leave request/approval/source consumer: Integrate policy publication with pending-request impacts | 3.24, 3.25-B, 3.34-A, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-G | Leave request/approval/source consumer: Integrate scheduled policy amendments and cancellations with pending requests | 3.24, 3.25-B, 3.35-A, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-I | Leave request/approval/source consumer: Integrate policy-assignment changes with pending requests | 3.24, 3.25-B, 3.36-A, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-M | Leave request/approval/source consumer: Integrate employee work-setting overrides and resets with pending requests | 2.22, 3.24, 3.25-B, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-O | Leave request/approval/source consumer: Integrate employee work-profile assignment with pending requests | 2.20, 3.24, 3.25-B, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-Q | Leave request/approval/source consumer: Integrate organization-default profile changes with pending requests | 2.21, 3.24, 3.25-B, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-S | Leave request/approval/source consumer: Integrate shared work-profile publication with pending requests | 2.23, 3.24, 3.25-B, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-U | Leave request/approval/source consumer: Integrate holiday-calendar changes with pending requests | 2.18, 3.24, 3.25-B, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.16-A | Leave request/approval/source consumer: Query my actionable approval queue and permitted inspection data | 3.24, 3.25-B, 5.18-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.17-A | Leave request/approval/source consumer: Query permitted team availability for request dates | 3.24, 3.25-B, 5.18-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.24-A | Leave request/approval/source consumer: Transfer selected unfinished approval steps through the protected API | 3.24, 3.25-B, 5.10-A, 5.10-B, 5.10-C, 5.18-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.5-A | Leave request/approval/source consumer: Record a scoped coverage exception and reassess pending finalization | 3.24, 3.25-B, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.28-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.4 | Leave correction: Calculate cancellation reversal and dependent earning effects | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1 | conditional-retain |
| 3.38 | Leave accounting/configuration/web: Restore an inactive leave type | 3.37 | bounded-remaining-delta-assessed |
| 5.16-B | Leave request/approval/source consumer: Browse my approval queue and inspect permitted requests | 3.24, 3.25-B, 5.16-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.24-C | Leave request/approval/source consumer: Integrate single-supervisor changes with unfinished approval transfers | 3.24, 3.25-B, 5.24-A, 5.28-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.2 | Leave correction: Expose minimum correction and deficit attention through the API | 3.18, 5.10-A, 5.10-B, 5.10-C, 5.15-A, 5.28-C, 6.1 | conditional-retain |
| 5.15-K | Leave request/approval/source consumer: Integrate employment end-date changes with pending Leave requests | 2.12, 3.24, 3.25-B, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.19-A, 5.24-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.17-B | Leave request/approval/source consumer: See permitted team availability in request review | 3.24, 3.25-B, 5.16-B, 5.17-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.24-E | Leave request/approval/source consumer: Integrate selected and planned supervisor replacement with approval transfers | 3.24, 3.25-B, 5.24-A, 5.24-C, 5.28-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.15 | Leave correction: Record reasoned deficit-review outcomes without erasing balances | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.2 | conditional-retain |
| 6.3 | Leave correction: Show minimum correction attention on Manage Leave | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.2 | conditional-retain |
| 5.23-A | Leave request/approval/source consumer: Process temporary expiry and authorized conditional return | 3.24, 3.25-B, 5.10-B, 5.24-A, 5.24-C, 5.24-E, 5.28-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.16 | Leave correction: Review deficits and follow permitted remedies | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.15, 6.3 | conditional-retain |
| 6.19 | Leave correction: Integrate approved and historical consequences of one-off balance adjustments | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1, 6.15, 6.2, 6.3 | conditional-retain |
| 6.21 | Leave correction: Integrate approved and historical consequences of recurring entitlement changes | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1, 6.15, 6.2, 6.3 | conditional-retain |
| 6.23 | Leave correction: Integrate approved and historical consequences of used-policy publication | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1, 6.15, 6.2, 6.3 | conditional-retain |
| 6.25 | Leave correction: Integrate approved and historical consequences of scheduled policy amendments and cancellations | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1, 6.15, 6.2, 6.3 | conditional-retain |
| 6.27 | Leave correction: Integrate approved and historical consequences of employee policy assignments | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1, 6.15, 6.2, 6.3 | conditional-retain |
| 6.29 | Leave correction: Integrate approved and historical consequences of employment periods and departure | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1, 6.15, 6.2, 6.3 | conditional-retain |
| 6.31 | Leave correction: Integrate approved and historical consequences of employee work-setting overrides and resets | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1, 6.15, 6.2, 6.3 | conditional-retain |
| 6.33 | Leave correction: Integrate approved and historical consequences of employee work-profile assignments | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1, 6.15, 6.2, 6.3 | conditional-retain |
| 6.35 | Leave correction: Integrate approved and historical consequences of organization-default work profiles | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1, 6.15, 6.2, 6.3 | conditional-retain |
| 6.37 | Leave correction: Integrate approved and historical consequences of shared work-profile publication | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1, 6.15, 6.2, 6.3 | conditional-retain |
| 6.39 | Leave correction: Integrate approved and historical consequences of holiday-calendar changes | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.1, 6.15, 6.2, 6.3 | conditional-retain |
| 5.21-A | Leave request/approval/source consumer: Create a bounded temporary appointment and apply its authorized pending work | 3.24, 3.25-B, 5.10-A, 5.10-B, 5.10-C, 5.16-A, 5.23-A, 5.24-A, 5.28-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.20 | Leave correction: Review approved and historical consequences of one-off balance adjustments | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.19 | conditional-retain |
| 6.22 | Leave correction: Review approved and historical consequences of recurring entitlement changes | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.21 | conditional-retain |
| 6.24 | Leave correction: Review approved and historical consequences of used-policy publication | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.23 | conditional-retain |
| 6.26 | Leave correction: Review approved and historical consequences of scheduled policy amendments and cancellations | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.25 | conditional-retain |
| 6.28 | Leave correction: Review approved and historical consequences of employee policy assignments | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.27 | conditional-retain |
| 6.30 | Leave correction: Review approved and historical consequences of employment periods and departure | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.29 | conditional-retain |
| 6.32 | Leave correction: Review approved and historical consequences of employee work-setting overrides and resets | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.31 | conditional-retain |
| 6.34 | Leave correction: Review approved and historical consequences of employee work-profile assignments | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.33 | conditional-retain |
| 6.36 | Leave correction: Review approved and historical consequences of organization-default work profiles | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.35 | conditional-retain |
| 6.38 | Leave correction: Review approved and historical consequences of shared work-profile publication | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.37 | conditional-retain |
| 6.40 | Leave correction: Review approved and historical consequences of holiday-calendar changes | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.39 | conditional-retain |
| 6.41 | Leave correction: Correct recorded employment dates through the existing People owner | 2.11, 2.12, 2.13, 3.18, 5.10-A, 5.10-B, 5.10-C, 5.15-K, 6.29 | conditional-retain |
| 5.22-A | Leave request/approval/source consumer: Extend a temporary appointment and safely postpone its return | 3.24, 3.25-B, 5.10-B, 5.21-A, 5.23-A, 5.28-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.25-A | Leave request/approval/source consumer: Restore outstanding supervisor review when recorded absence ends | 3.24, 3.25-B, 5.10-B, 5.18-A, 5.21-A, 5.24-C, 5.28-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.42 | Leave correction: Review a factual employment-date correction and its Leave consequences | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.30, 6.41 | conditional-retain |
| 5.11-A | Leave request/approval/source consumer: Submit my own leave request through the protected API | 3.24, 3.25-B, 3.28, 5.10-A, 5.10-B, 5.10-C, 5.15-A, 5.15-C, 5.15-E, 5.15-G, 5.15-I, 5.15-K, 5.15-M, 5.15-O, 5.15-Q, 5.15-S, 5.15-U, 5.21-A, 5.24-C, 5.24-E, 5.25-A, 5.28-C, E1-ACCESS-B, E1-D2-B, E1-WRITE | conditional-retain |
| 5.22-C | Leave request/approval/source consumer: End temporary authority early and resolve its unfinished work | 3.24, 3.25-B, 5.10-B, 5.21-A, 5.22-A, 5.23-A, 5.24-A, 5.28-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.26-A | Leave request/approval/source consumer: Generate recurring reminders for currently actionable approvals | 3.24, 3.25-B, 5.18-A, 5.19-A, 5.21-A, 5.23-A, 5.24-A, 5.25-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.5 | Leave correction: Cancel approved leave through one protected command | 3.18, 3.24, 3.25-B, 5.10-A, 5.10-B, 5.10-C, 5.25-A, 6.2, 6.3, 6.4 | conditional-retain |
| 5.11-B | Leave request/approval/source consumer: Submit through Apply and see the confirmed result | 3.24, 3.25-B, 5.11-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.12-A | Leave request/approval/source consumer: Record on-behalf leave and accept the initial employee response through the API | 3.24, 3.25-B, 5.10-B, 5.11-A, 5.18-A, 5.19-A, 5.28-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.27-A | Leave request/approval/source consumer: Escalate overdue approvals once and expose current manager attention | 3.24, 3.25-B, 5.24-A, 5.26-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.6 | Leave correction: Review and confirm approved-leave cancellation | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.5 | conditional-retain |
| 8.18 | Leave import/qualification: Demonstrate bounded worker drain, forced stop and recovery | 3.24, 5.23-A, 5.26-A, E1-ACCESS-B, E1-ENV | conditional-retain |
| 5.13-A | Leave request/approval/source consumer: Confirm exceptional allocation and optional approval through the API | 3.24, 3.25-B, 5.10-B, 5.12-A, 5.18-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-B | Leave request/approval/source consumer: Review pending-request impacts before confirming a balance adjustment | 3.24, 3.25-B, 3.29, 5.11-B, 5.15-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-D | Leave request/approval/source consumer: Review pending-request impacts of recurring entitlement changes | 3.24, 3.25-B, 3.30, 5.11-B, 5.15-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-F | Leave request/approval/source consumer: Review pending-request impacts in policy publication | 3.24, 3.25-B, 3.34-B, 5.11-B, 5.15-E, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-H | Leave request/approval/source consumer: Review pending impacts of scheduled policy amendments and cancellations | 3.24, 3.25-B, 3.35-B, 5.11-B, 5.15-G, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-J | Leave request/approval/source consumer: Review pending-request impacts of policy-assignment changes | 3.24, 3.25-B, 3.36-B, 5.11-B, 5.15-I, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-L | Leave request/approval/source consumer: Review Leave consequences before confirming an employment end date | 2.12, 3.24, 3.25-B, 5.11-B, 5.15-K, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-N | Leave request/approval/source consumer: Review pending-request impacts of employee work-setting overrides | 2.22, 3.24, 3.25-B, 5.11-B, 5.15-M, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-P | Leave request/approval/source consumer: Review pending-request impacts of employee profile assignment | 2.20, 3.24, 3.25-B, 5.11-B, 5.15-O, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-R | Leave request/approval/source consumer: Review pending-request impacts of organization-default profile changes | 2.21, 3.24, 3.25-B, 5.11-B, 5.15-Q, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-T | Leave request/approval/source consumer: Review pending-request impacts of shared work-profile publication | 2.23, 3.24, 3.25-B, 5.11-B, 5.15-S, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.15-V | Leave request/approval/source consumer: Review pending-request impacts of holiday-calendar changes | 2.18, 3.24, 3.25-B, 5.11-B, 5.15-U, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.18-B | Leave request/approval/source consumer: Approve or reject from completed request review | 3.24, 3.25-B, 5.12-A, 5.16-B, 5.17-B, 5.18-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.19-B | Leave request/approval/source consumer: Withdraw my pending request from its details | 3.24, 3.25-B, 5.11-B, 5.19-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.20-A | Leave request/approval/source consumer: Preserve corrections and resubmit a rejected request through the API | 3.24, 3.25-B, 5.10-B, 5.11-A, 5.12-A, 5.18-A, 5.28-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.21-B | Leave request/approval/source consumer: Appoint a temporary approver through the reviewed appointment screen | 3.24, 3.25-B, 5.11-B, 5.16-B, 5.21-A, 5.23-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.24-B | Leave request/approval/source consumer: Review and confirm manual reassignment of selected approvals | 3.24, 3.25-B, 5.11-B, 5.24-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.24-D | Leave request/approval/source consumer: Show Leave consequences in single-supervisor editing | 3.24, 3.25-B, 5.11-B, 5.24-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.24-F | Leave request/approval/source consumer: Review selected supervisor replacements and their Leave outcomes | 3.24, 3.25-B, 5.11-B, 5.24-E, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.28-A | Leave request/approval/source consumer: Complete residual coverage-attention reads after the first-use projection | 3.24, 3.25-B, 5.21-A, 5.22-C, 5.23-A, 5.24-C, 5.24-E, 5.25-A, 5.27-A, 5.28-C, 5.5-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.5-B | Leave request/approval/source consumer: Record a reasoned exception from existing request and coverage details | 3.24, 3.25-B, 5.11-B, 5.5-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 8.20 | Leave import/qualification: Demonstrate alert thresholds and verified incident recovery | 8.18, 8.19, E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.23 | Leave import/qualification: Reconcile restored notification work before resuming outbound effects | 8.18, 8.22, E1-ACCESS-B, E1-ENV | conditional-retain |
| 5.12-B | Leave request/approval/source consumer: Submit for an employee and complete the initial response in the browser | 3.24, 3.25-B, 5.11-B, 5.12-A, 5.19-B, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.20-B | Leave request/approval/source consumer: Edit and resubmit a rejected request in the browser | 3.24, 3.25-B, 5.11-B, 5.20-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.22-B | Leave request/approval/source consumer: Extend a temporary appointment from its details | 3.24, 3.25-B, 5.21-B, 5.22-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.22-D | Leave request/approval/source consumer: End a temporary appointment early from its details | 3.24, 3.25-B, 5.21-B, 5.22-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.27-B | Leave request/approval/source consumer: Show escalated approvals in Manage Leave Needs attention | 3.24, 3.25-B, 5.11-B, 5.24-B, 5.27-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.30-A | Leave request/approval/source consumer: Complete own-request details and formal-history reads | 3.24, 3.25-B, 5.11-A, 5.12-A, 5.13-A, 5.18-A, 5.19-A, 5.20-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.32-I | Leave request/approval/source consumer: Verify temporary appointment from effective start through expiry | 3.24, 3.25-B, 5.16-B, 5.18-B, 5.21-B, 5.23-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.32-J | Leave request/approval/source consumer: Verify supervisor-step restoration when recorded absence ends | 3.24, 3.25-B, 5.16-B, 5.18-B, 5.25-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.7 | Leave correction: Track administrative correction follow-up at its real lifecycle producers | 3.18, 5.10-A, 5.10-B, 5.10-C, 5.18-A, 5.20-A, 6.2 | conditional-retain |
| 5.13-B | Leave request/approval/source consumer: Review exceptional funding and confirm the permitted action | 3.24, 3.25-B, 5.12-B, 5.13-A, 5.18-B, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.28-B | Leave request/approval/source consumer: Complete coverage-attention composition and existing remedy navigation | 3.24, 3.25-B, 5.21-B, 5.24-B, 5.27-B, 5.28-A, 5.28-C, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.29-A | Leave request/approval/source consumer: Query my year-based leave calendar and history list | 3.24, 3.25-B, 5.30-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.30-B | Leave request/approval/source consumer: Complete existing request details with secondary formal History | 3.24, 3.25-B, 5.11-B, 5.12-B, 5.19-B, 5.20-B, 5.30-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.32-K | Leave request/approval/source consumer: Verify recurring reminders and one-time manager escalation together | 3.24, 3.25-B, 5.18-B, 5.26-A, 5.27-B, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.8 | Leave correction: Present correction follow-up in existing attention and details | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.3, 6.7 | conditional-retain |
| 5.29-B | Leave request/approval/source consumer: Browse my leave in Calendar and List views | 3.24, 3.25-B, 5.29-A, 5.30-B, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.32-C | Leave request/approval/source consumer: Verify rejected correction and same-request fresh-cycle resubmission | 3.24, 3.25-B, 5.18-B, 5.20-B, 5.30-B, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.32-F | Leave request/approval/source consumer: Verify employment-end consequences across People and Leave | 3.24, 3.25-B, 5.15-L, 5.18-B, 5.30-B, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.32-G | Leave request/approval/source consumer: Verify used-policy publication and pending-request consequences | 3.24, 3.25-B, 5.15-F, 5.18-B, 5.30-B, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.32-H | Leave request/approval/source consumer: Verify required documents through actual submission and final approval | 3.24, 3.25-B, 5.11-B, 5.18-B, 5.30-B, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.32-L | Leave request/approval/source consumer: Verify original submission recovery after its response is lost | 3.24, 3.25-B, 5.11-B, 5.30-B, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.9 | Leave correction: Atomically cancel and submit a linked replacement | 3.18, 4.4-L, 5.10-A, 5.10-B, 5.10-C, 5.11-A, 5.12-A, 6.5, 6.7, 6.8 | conditional-retain |
| 5.31-A | Leave request/approval/source consumer: Compose current leave and required responses on My Leave | 3.24, 3.25-B, 5.11-B, 5.12-B, 5.19-B, 5.20-B, 5.29-B, 5.30-B, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.10 | Leave correction: Change my approved leave through the existing request form | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.6, 6.9 | conditional-retain |
| 6.11 | Leave correction: Correct another employee’s approved leave under administrative authority | 3.18, 4.4-L, 5.10-A, 5.10-B, 5.10-C, 5.11-A, 5.12-A, 6.9 | conditional-retain |
| 5.32-A | Leave request/approval/source consumer: Verify a funded own-request journey through final approval | 3.24, 3.25-B, 5.11-B, 5.18-B, 5.30-B, 5.31-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.32-B | Leave request/approval/source consumer: Verify on-behalf submission and the initial employee unpaid response | 3.24, 3.25-B, 5.12-B, 5.18-B, 5.30-B, 5.31-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.32-D | Leave request/approval/source consumer: Verify employee withdrawal and connected pending-work closure | 3.24, 3.25-B, 5.12-B, 5.16-B, 5.19-B, 5.31-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 5.32-E | Leave request/approval/source consumer: Verify a one-off balance adjustment against a pending request | 3.24, 3.25-B, 5.15-B, 5.18-B, 5.30-B, 5.31-A, E1-ACCESS-B, E1-WRITE | conditional-retain |
| 6.12 | Leave correction: Review an administrative correction and its employee explanation | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.10, 6.11 | conditional-retain |
| 6.13 | Leave correction: Allow scoped administrators to preserve and resubmit rejected corrections | 3.18, 4.4-L, 5.10-A, 5.10-B, 5.10-C, 5.11-A, 5.12-A, 6.11, 6.7 | conditional-retain |
| 6.14 | Leave correction: Resume rejected administrative corrections from follow-up | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.12, 6.13, 6.8 | conditional-retain |
| 6.17 | Leave correction: Complete linked correction and calculation-history reads | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.11, 6.13, 6.15, 6.9 | conditional-retain |
| 6.18 | Leave correction: Explain corrected leave in employee history and calendars | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.10, 6.12, 6.14, 6.16, 6.17 | conditional-retain |
| 7.1 | Leave report/read: Read the scoped organization absence overview | 2.26, 3.17-B, 4.7, 5.10-A, 5.30-A, 6.17, 6.9, E1-ACCESS-B, E1-PEOPLE | conditional-retain |
| 7.11 | Leave report/read: Query leave used by employee, type, team and period reports | 2.26, 3.17-B, 5.10-A, 5.30-A, 6.17, E1-ACCESS-B, E1-PEOPLE | conditional-retain |
| 7.13 | Leave report/read: Query upcoming absence reports | 2.26, 3.17-B, 5.10-A, 5.30-A, 6.17, E1-ACCESS-B, E1-PEOPLE | conditional-retain |
| 7.15 | Leave report/read: Query pending approval aging reports | 2.26, 3.17-B, 5.10-A, 5.18-A, 5.26-A, 5.30-A, 6.17, E1-ACCESS-B, E1-PEOPLE | conditional-retain |
| 7.17 | Leave report/read: Query overrides and administrative adjustments reports | 2.26, 3.17-B, 5.10-A, 5.30-A, 6.17, E1-ACCESS-B, E1-PEOPLE | conditional-retain |
| 7.7 | Leave report/read: Query current and corrected point-in-time balance reports | 2.26, 3.17-B, 5.10-A, 5.30-A, 6.17, E1-ACCESS-B, E1-PEOPLE | conditional-retain |
| 7.9 | Leave report/read: Query accrual and adjustment history reports | 2.26, 3.17-B, 5.10-A, 5.30-A, 6.17, E1-ACCESS-B, E1-PEOPLE | conditional-retain |
| 6.43 | Leave correction: Verify cancellation and own replacement across real boundaries | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.10, 6.18, 6.6 | conditional-retain |
| 6.44 | Leave correction: Verify administrative correction rejection and follow-up recovery | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.12, 6.14, 6.18 | conditional-retain |
| 6.45 | Leave correction: Verify historical corrections and deficit outcomes through actual owners | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.16, 6.18, 6.20, 6.22, 6.24, 6.26, 6.28, 6.30, 6.32, 6.34, 6.36, 6.38, 6.40, 6.42 | conditional-retain |
| 7.19 | Leave report/read: Generate an audited CSV from all matching authorized report rows | 5.10-A, 7.11, 7.13, 7.15, 7.17, 7.7, 7.9, E1-ACCESS-B | conditional-retain |
| 7.2 | Leave report/read: Browse the organization timeline without changing leave by dragging | 4.7, 5.10-A, 6.9, 7.1, E1-ACCESS-B | conditional-retain |
| 7.4 | Leave report/read: Remember overview filters within the current account and organization | 5.10-A, 5.29-A, 7.1, E1-ACCESS-B | conditional-retain |
| 8.3 | Leave import/qualification: Reconcile opening balances and transferred request effects in preview | 3.18, 3.9, 5.8-A, 7.7, 8.1, 8.2, E1-ACCESS-B, E1-ENV | conditional-retain |
| 6.46 | Leave correction: Verify correction compatibility and recoverable release evidence | 3.18, 5.10-A, 5.10-B, 5.10-C, 6.43, 6.44, 6.45 | conditional-retain |
| 7.3 | Leave report/read: Use the date-grouped overview and staged filters on mobile | 4.7, 5.10-A, 6.9, 7.1, 7.2, E1-ACCESS-B | conditional-retain |
| 8.4 | Leave import/qualification: Bind client email approval to the exact import preview | 8.3, E1-ACCESS-B, E1-ENV | conditional-retain |
| 7.5 | Leave report/read: Restore applied overview filters with truthful preference feedback | 5.10-A, 7.3, 7.4, E1-ACCESS-B | conditional-retain |
| 7.6 | Leave report/read: Complete existing management navigation to overview and records | 5.10-A, 5.27-B, 6.3, 6.8, 7.2, 7.3, E1-ACCESS-B | conditional-retain |
| 8.5 | Leave import/qualification: Apply reconciled opening portions through the accounting owner | 3.18, 3.9, 5.8-A, 7.7, 8.3, 8.4, E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.8 | Leave import/qualification: Prepare imported documents through the existing Content owner | 4.12-S, 4.4-L, 4.4-S, 4.7, 8.2, 8.4, E1-ACCESS-B, E1-ENV | conditional-retain |
| 7.27 | Leave report/read: Search audit history and inspect permitted before and after | 5.10-A, 7.26, 7.6, E1-ACCESS-B | conditional-retain |
| 7.29 | Leave report/read: Verify organization overview privacy and accessible navigation | 5.10-A, 7.5, 7.6, E1-ACCESS-B | conditional-retain |
| 7.8 | Leave report/read: Read balance reports in the first shared reporting layout | 5.10-A, 7.6, 7.7, E1-ACCESS-B | conditional-retain |
| 8.6 | Leave import/qualification: Adopt recorded historical and approved requests with explicit provenance | 2.26, 5.10-A, 6.17, 8.2, 8.4, 8.5, E1-ACCESS-B, E1-ENV, E1-ID-B, E1-PEOPLE | conditional-retain |
| 7.10 | Leave report/read: Browse accrual and adjustment history results | 5.10-A, 7.8, 7.9, E1-ACCESS-B | conditional-retain |
| 7.12 | Leave report/read: Browse leave used by employee, type, team and period results | 5.10-A, 7.11, 7.8, E1-ACCESS-B | conditional-retain |
| 7.14 | Leave report/read: Browse upcoming absence results | 5.10-A, 7.13, 7.8, E1-ACCESS-B | conditional-retain |
| 7.16 | Leave report/read: Browse pending approval aging results | 5.10-A, 7.15, 7.8, E1-ACCESS-B | conditional-retain |
| 7.18 | Leave report/read: Browse overrides and administrative adjustments results | 5.10-A, 7.17, 7.8, E1-ACCESS-B | conditional-retain |
| 7.30 | Leave report/read: Verify cross-owner audit chronology and private detail access | 5.10-A, 7.27, E1-ACCESS-B | conditional-retain |
| 8.17 | Leave import/qualification: Qualify accessible role journeys on supported browsers | 7.27, E1-ACCESS-B, E1-D5, E1-ENV | conditional-retain |
| 8.7 | Leave import/qualification: Import pending requests into a freshly verified approval cycle | 2.26, 5.10-B, 5.11-A, 5.12-A, 5.18-A, 8.2, 8.4, 8.5, 8.6, E1-ACCESS-B, E1-ENV, E1-ID-B, E1-PEOPLE | conditional-retain |
| 7.20 | Leave report/read: Export each report with clear progress and retry feedback | 5.10-A, 7.10, 7.12, 7.14, 7.16, 7.18, 7.19, E1-ACCESS-B | conditional-retain |
| 8.9 | Leave import/qualification: Apply one approved employee import atomically through Leave | 8.4, 8.5, 8.6, 8.7, 8.8, E1-ACCESS-B, E1-ENV | conditional-retain |
| 7.28 | Leave report/read: Verify all six report and CSV definitions through actual consumers | 5.10-A, 7.10, 7.12, 7.14, 7.16, 7.18, 7.20, 7.8, E1-ACCESS-B | conditional-retain |
| 8.10 | Leave import/qualification: Resume imports using original employee operation outcomes | 8.9, E1-ACCESS-B, E1-ENV | conditional-retain |
| 7.31 | Leave report/read: Qualify reporting bounds, compatibility and read-only operation | 5.10-A, 7.28, 7.29, 7.30, E1-ACCESS-B | conditional-retain |
| 8.11 | Leave import/qualification: Reconcile applied records against the exact approved batch | 3.18, 3.9, 5.8-A, 7.7, 8.10, E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.15 | Leave import/qualification: Qualify cross-organization security through real owner boundaries | 7.28, 7.29, 7.30, E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.12 | Leave import/qualification: Reconcile export-to-cutover changes before final approval | 8.11, E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.24 | Leave import/qualification: Qualify coordinated migrations and recoverable release activation | 7.31, E1-ACCESS-B, E1-ENV, E1-VERIFY | conditional-retain |
| 8.25 | Leave import/qualification: Measure representative application and import workloads | 7.31, E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.13 | Leave import/qualification: Release only current actionable imported-work notifications at activation | 3.24, 3.25-B, 5.26-A, 8.10, 8.12, 8.7, E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.27 | Leave import/qualification: Prepare support and operational handover from verified procedures | 8.20, 8.22, 8.23, 8.24, E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.14 | Leave import/qualification: Verify import arithmetic, atomic apply and interruption recovery | 8.11, 8.12, 8.13, E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.26 | Leave import/qualification: Run representative human acceptance for each role | 8.14, 8.15, 8.16, 8.17, 8.25, E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.28 | Leave import/qualification: Assemble the pilot release evidence and go/no-go decision | 8.11, 8.12, 8.14, 8.15, 8.16, 8.17, 8.18, 8.19, 8.20, 8.21, 8.22, 8.23, 8.24, 8.25, 8.26, 8.27, E1-ACCESS-B, E1-ENV | conditional-retain |
| 8.29 | Leave import/qualification: Enable the approved pilot through existing access and discovery owners | 2.1, 8.13, 8.28, E1-ACCESS-B, E1-DISCOVERY, E1-ENV, E1-LAUNCHER | conditional-retain |
| 8.30 | Leave import/qualification: Verify pilot health and record operational acceptance | 8.29, E1-ACCESS-B, E1-ENV | conditional-retain |

## Assessment meaning

`conditional-retain` counts only the declared incremental outcome using completed
actual predecessors, plus its scoped API/native/browser/failure/generated-client and
five-impact evidence. It is not a final small-size PASS while a concrete contract or
actual remaining shared delta is unknown. Existing E5/E6/E7/E8 item assessments are
referenced, not rerun from their title. The 98 E1–E3 and seventeen E4 leaves now have explicit per-item
remaining-delta and critical scope judgments in the linked assessments. G01 coverage
reconciliation remains open; none of these tags authorizes implementation.
No source criterion is deleted to make this table fit.

`bounded-remaining-delta-assessed` links all 98 E1–E3 leaves to the early assessment.
`bounded-owner-delta-assessed` links all seventeen E4 leaves to the owner assessment
and exact parent-clause allocation. Selected technical models remain consolidated-review
candidates, with actual provider/session/retention proof at delivery. E4 children
keep the parent as coverage rather than another implementation item.
Shared streaming is E1-CONTENT-READ, not rebuilt in 4.7; retirement 4.14 follows actual
PtS/Expense caller proof, not future Leave 4.13. These avoid duplicate work and cycles.

The five impacts apply at every first consumer: prove/reuse neutral scaffold/fixtures
and maintain generated sources, reuse/promote only proven neutral shared UI, update
actual generated guidance when commands change, synchronize owning docs/traceability,
and retain accepted ADRs or record a linked change when required. No universal runtime
engine or extra generic workflow is introduced by this register.
