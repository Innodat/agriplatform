### Continuous changes have no verification of the two-second persistence bound

- **Changed surface:** `apps/scribeswell/web/src/context/ReaderWorkspaceContext.tsx:50–53` adds a 250ms debounce and a two-second maximum wait, required by `apps/scribeswell/docs/WORKSPACE_RESTORATION_V1.md:46`.
- **Impacted consumer or site:** Reader scroll checkpoints invoke this scheduler through `apps/scribeswell/web/src/hooks/useReaderWorkspace.ts:160–161`.
- **Existing test evidence:** `Regression gap`: repository-wide symbol/import-reference searches found storage coverage in `workspace-restoration.spec.cjs` and `personal-notes.spec.cjs`. The scroll test at `workspace-restoration.spec.cjs:179` performs one scroll and waits for persistence. The lifecycle tests at line 269 explicitly flush after one change. The checkpoint helper at `personal-notes.spec.cjs:117` polls after input settles. None of these tests keeps checkpoints arriving faster than the debounce while asserting a durable write.
- **Missing verification:** Assert that IndexedDB receives the latest eligible projection within two seconds while changes continue, without a lifecycle flush.
- **Demonstration:** Removing the maximum-wait timer at `ReaderWorkspaceContext.tsx:53` leaves ordinary settled-input and lifecycle tests passing. Repeated checkpoints less than 250ms apart would then postpone persistence indefinitely.
- **Consequence:** Sustained reading activity can leave remembered position stale until activity stops; the checked tests would not catch this regression.
- **Disposition:** `patch` — add a paused-clock Playwright case to `workspace-restoration.spec.cjs` that generates repeated eligible changes under 250ms apart and checks the stored projection at the two-second boundary. 
