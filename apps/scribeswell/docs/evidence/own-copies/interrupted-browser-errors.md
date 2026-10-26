apps/scribeswell/web/test-results/personal-notes-copies-revi-93a54-h-until-explicit-use-latest-desktop/error-context.md

# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: personal-notes.spec.cjs >> copies: review latest preserves the local branch until explicit use latest
- Location: tests/personal-notes.spec.cjs:1655:1

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Add note', exact: true })
    - waiting for "http://127.0.0.1:5182/" navigation to finish...
    - navigated to "http://127.0.0.1:5182/"

```



apps/scribeswell/web/test-results/personal-notes-copies-high-09cf0-es-the-failed-fork-identity-desktop/error-context.md

# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: personal-notes.spec.cjs >> copies: highlight_proof_unavailable keeps local writing and retires the failed fork identity
- Location: tests/personal-notes.spec.cjs:1741:76

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('alert').filter({ hasText: 'Copy was not saved' })
Expected: visible
Error: strict mode violation: getByRole('alert').filter({ hasText: 'Copy was not saved' }) resolved to 2 elements:
    1) <p role="alert">…</p> aka getByText('Copy was not saved. Your').first()
    2) <p role="alert">Copy was not saved. Your input is kept. Review th…</p> aka getByText('Copy was not saved. Your input is kept. Review the source before trying again.', { exact: true })

Call log:
  - Expect "toBeVisible" getByRole('alert').filter({ hasText: 'Copy was not saved' }) with timeout 5000ms
  - waiting for getByRole('alert').filter({ hasText: 'Copy was not saved' })

```



apps/scribeswell/web/test-results/personal-notes-copies-note-f24bf-es-the-failed-fork-identity-desktop/error-context.md

# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: personal-notes.spec.cjs >> copies: note_base_unavailable keeps local writing and retires the failed fork identity
- Location: tests/personal-notes.spec.cjs:1741:76

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('alert').filter({ hasText: 'original base is unavailable' })
Expected: visible
Error: strict mode violation: getByRole('alert').filter({ hasText: 'original base is unavailable' }) resolved to 2 elements:
    1) <p role="alert">…</p> aka getByText('This note’s original base is unavailable. Your input is kept. Retry Studies')
    2) <p role="alert">This note’s original base is unavailable. Your in…</p> aka getByText('This note’s original base is unavailable. Your input is kept.', { exact: true })

Call log:
  - Expect "toBeVisible" getByRole('alert').filter({ hasText: 'original base is unavailable' }) with timeout 5000ms
  - waiting for getByRole('alert').filter({ hasText: 'original base is unavailable' })

```



apps/scribeswell/web/test-results/personal-notes-copies-Save-6caec--without-overwriting-latest-desktop/error-context.md

# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: personal-notes.spec.cjs >> copies: Save mine freezes original base and complete local value without overwriting latest
- Location: tests/personal-notes.spec.cjs:1710:1

# Error details

```
Error: expect(locator).toHaveAttribute(expected) failed

Locator:  getByRole('tablist', { name: 'Workspace tabs' })
Expected: "true"
Received: "false"
Timeout:  5000ms

Call log:
  - Expect "toHaveAttribute" getByRole('tablist', { name: 'Workspace tabs' }) with timeout 5000ms
  - waiting for getByRole('tablist', { name: 'Workspace tabs' })
    5 × locator resolved to <div role="tablist" data-device-ready="false" aria-label="Workspace tabs" class="flex max-w-full overflow-x-auto gap-1 items-center">…</div>
      - unexpected value "false"

```

