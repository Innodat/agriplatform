# Numeric email-code template candidate

This shared opt-in fixture supports KDG's selected existing-account Supabase Auth
flow. It is not installed, merged, mounted or sent by any command. Native ENV
preparation and historical closed GoTrue inputs remain unchanged. Other applications
may adopt the proven pattern deliberately; it is not the default sign-in method.

`config.toml` is a fragment for a future disposable project's `supabase/config.toml`.
Its `content_path` is relative to that project's root; `sign-in.html` would need to
exist at `supabase/templates/sign-in.html`. No present preparation or generator
copies it there. Do not use the fragment as a standalone Supabase configuration.

The email template uses only `{{ .Token }}` with no sign-in URL, token hash, personal
metadata, external assets or app-specific branding. Six digits and 3600 seconds retain
the already selected email defaults. The 60-second resend intent aligns with the
current browser controller; its guard is advisory and resets on full reload/unmount.
The server must enforce its own limits. The template makes no delivery-time or remaining-
lifetime promise and contains no code value until the Auth server renders it.

There are two different switches: the CLI maps `auth.email.enable_signup=true` to
`GOTRUE_EXTERNAL_EMAIL_ENABLED=true`, which enables email login. Global
`auth.enable_signup=false` maps to `GOTRUE_DISABLE_SIGNUP=true`, preventing new signup.
The consuming SDK must also send `shouldCreateUser:false`. Anonymous sign-in and manual
linking stay off. Account existence, email confirmation and access provisioning are not
established by this fixture; current KDG API checks remain mandatory.

The selected CLI 2.120.0 pure builders produce a `MAGIC_LINK` template URL on Kong's
internal port 8088 and a matching `/home/kong/templates/email/magic_link.html` mount
intent. The publisher mount is `rw,z`; this fixture does not apply it. The test manually
supplies resolved input and an absolute synthetic mount path, and does not run the
CLI's config parser, path reader, environment overrides, container lifecycle or Auth.

From repository root, select an existing qualified Node 26.11.1 artifact:

```sh
KDG_EMAIL_CODE_REQUIRE_PUBLISHER=1 \
KDG_PROFILE_TOOLCHAIN_RUN_ID=<qualified-tool-artifact-UUID> \
PYTHONPATH=platform/deployment:platform/deployment/tests \
<selected-python3.15> -m unittest -v test_email_code_contract
```

The tool selector is validated against its existing receipt and payload fingerprint;
no tools are installed. Without it, unittest explicitly skips the publisher comparison;
that skip is not qualification. Set KDG_EMAIL_CODE_REQUIRE_PUBLISHER=1 to fail if
the artifact selector is missing; qualification and CI evidence must include all five tests passing with zero skips.
The checks are platform-owned and reusable; applications should reference this suite
rather than duplicate it. Upstream source snapshots are verified before relocation;
only imports are adapted for offline pure-builder execution. No dependencies change.

| Scenario | Established now | Still requires Auth/runtime qualification |
| --- | --- | --- |
| Send code | Token-only artifact and template/config mapping | SMTP sink receipt, actual Auth rendering, no unexpected external route |
| Existing account | Signup-off/provider-on intent; client already sends create_user:false | Real server behavior for existing/unknown/unconfirmed accounts without creating accounts |
| Resend/non-delivery |60-second intent; current UI has safe resend/wait feedback | Delivery failure, throttling and old/new-code behavior under actual server timing |
| Invalid/expired/used code | Existing KDG injected SDK error handling remains evidence | Server expiry, one-use enforcement and replay refusal; no simulation substitutes |
| Session recovery | Existing SDK persistence/current-access proof remains evidence | Auth-backed refresh/logout/reload over the selected target and device |

Sources: [Supabase passwordless email](https://supabase.com/docs/guides/auth/auth-email-passwordless),
[local email templates](https://supabase.com/docs/guides/local-development/customizing-email-templates),
and pinned Auth 2.197.0 [email-provider guard](https://github.com/supabase/auth/blob/4eee58f296d9698a1c2c0ae14d7a0b379c7622d3/internal/api/magic_link.go#L43)
and [create_user check](https://github.com/supabase/auth/blob/4eee58f296d9698a1c2c0ae14d7a0b379c7622d3/internal/api/otp.go#L75).
CLI mapping and mount authority are the existing hash-verified source manifests in
`../supabase-gotrue-source` and `../supabase-kong-source`. Those historical bytes stay
immutable. Current online docs explain semantics; they do not qualify the pinned runtime.
