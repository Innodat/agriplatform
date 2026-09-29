# First coordinated production activation

Prepared 2026-09-29. Public activation awaits the owner's explicit approval after
the completed acceptance checks. The isolated storage-expiry check passed and
its temporary objects were removed. This is an operational plan for
existing delivery tooling, not a new release workflow.

## Candidate and target

The application/tooling baseline is e974ae4. The final documentation commit carrying
this plan and completed acceptance evidence will be identified in the approval
request. Remote main was inspected at 4cffad16ddf4dcb1bd658a0093c67431072dad7e.
The push must be a normal fast-forward; stop and inspect if remote main changed.
It publishes the previously implemented PtS/Scribeswell and platform deployment
work together, not only the final documentation changes.

- Hetzner boabab, existing host 138.199.217.158, private WireGuard deployment access.
- Existing Supabase project gjbsnxmbhxsvcblzgfts; existing imported data and users.
- Existing Netlify site boabab, scribeswell.com; APISIX at api.scribeswell.com.
- PtS at https://scribeswell.com/; public Hebrew reader at
  https://scribeswell.com/scribeswell/; launcher connects both applications.
- No new server, provider plan or separate database. Existing service usage applies.

## Approved activation would do

1. Recheck clean candidate checkout, remote main, actual database revisions and
   installed target configuration against the recorded evidence. Create/install the
   root-only bootstrap assertion with the current schema/migration fingerprints and
   an explicit reference to the owner's activation approval. Do not set verification
   flags until their supporting checks passed. Keep a local protected evidence copy.
2. Push the exact candidate commit to main. Its existing production workflow becomes
   active: validate/build/test, publish immutable API images to GHCR, connect over
   WireGuard, then run coordinated owner migrations before service activation.
   Current expected heads are access_0001,content_0004,pts_0001; no new schema SQL or
   import is expected. Unexpected migration drift blocks activation for inspection.
3. Start the five registered services (directory, access, content, PtS, Scribeswell)
   behind APISIX using scoped dual-stack bridges. Only gateway 443 is public; Access,
   Content and database credentials remain private. Verify API health and routing.
4. Only after API activation passes, publish the assembled frontend to Netlify.
   Both apps contain the actual Supabase public key/project and api.scribeswell.com
   endpoints. No localhost/placeholder Auth targets or protected source files.
   Keep native Netlify builds paused: the GitHub workflow owns future publication.
5. Verify the published revision, HTTPS routes, public Bible passage, protected API
   denial, frontend asset paths and shared-session flows. User confirms ordinary
   password sign-in on the live origin. No operator changes the user's password.
   Recovery-email delivery is already confirmed; consuming a recovery link and
   actually changing a password is a separate user action, not claimed by these tests.

## Evidence and limits

See PRODUCTION_STATUS.md for actual Auth, collection, restricted-role, storage,
network, backup/restore and migration results. Private scripts/result files under
.local/production-infrastructure contain operation evidence; no credentials or
signed URLs are included in tracked documents. Original source material and private
operation files are excluded from the Git archive/frontend publish directory.

The production-configured frontend builds and passes assembled-artifact browser
acceptance; 24 login/recovery and 11 shared-session tests passed with local fixtures.
Actual production Auth/session claims, current permission revocation/restoration,
source byte integrity and signed-read expiry have been checked independently.
Do not equate fixture tests with an already published working application.

## Failure and recovery

CI serializes releases; host locking spans migration and activation. A migration
failure blocks application activation and later publication. Preserve owner evidence
and reconcile actual revisions; never reverse migrations automatically. Uncertain
migration outcomes require operator reconciliation before retry (durable retry gating
is tracked as follow-up). The first release has no earlier live API stack to restore.

Netlify's previous deploy is 6aba06e3dac3132bd6edcc1a, the known broken standalone build.
Retaining/reverting it restores the previous public state, not a working platform.
If API activation succeeds but frontend publication fails, retain the successful APIs
and retry the saved frontend artifact under the documented deployment hold; a workflow
rerun creates new image candidates and is not exact-artifact recovery. If new APIs must
be stopped, identify only this release's Compose project, preserve database/storage,
certificates and evidence, and obtain approval for the concrete recovery action.

No public success claim until the final route and frontend verification passes.
