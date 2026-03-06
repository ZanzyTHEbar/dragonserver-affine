# AFFiNE Troubleshooting

This guide covers the most likely DragonServer deployment issues for AFFiNE on Coolify.

## 1. `affine_migration` shows unhealthy or exited

**Expected behavior:** `affine_migration` is a one-shot predeploy job. It should run once, finish successfully, and exit.

**Fix:** Ensure the compose uses:

- `exclude_from_hc: true` on `affine_migration`
- `restart: "no"` on `affine_migration`
- `depends_on.affine_migration.condition=service_completed_successfully` on `affine`

If the migration job actually failed, inspect its logs in Coolify before retrying the deploy.

## 2. OIDC login loops or callback fails

Check all of the following:

- Authentik redirect URI is exactly `https://docs.zacariahheim.com/oauth/callback`
- AFFiNE OIDC issuer is `https://auth.zacariahheim.com/application/o/affine/`
- `AFFINE_SERVER_EXTERNAL_URL` matches the real public URL
- Coolify domain is assigned to the `affine` service as `https://docs.zacariahheim.com:3010`

If any of those differ, generated URLs or callback handling can break.

## 3. Generated links point to the wrong host

This is usually an external URL mismatch.

Verify:

- `AFFINE_SERVER_HOST=docs.zacariahheim.com`
- `AFFINE_SERVER_HTTPS=true`
- `AFFINE_SERVER_EXTERNAL_URL=https://docs.zacariahheim.com`

Redeploy after correcting them.

## 4. Search is missing or broken

AFFiNE full-text search depends on the indexer.

Verify:

- `AFFINE_INDEXER_ENABLED=true`
- `AFFINE_INDEXER_SEARCH_ENDPOINT=http://indexer:9308`
- the `indexer` service is healthy
- `MANTICORE_DATA_LOCATION` points to persistent storage

If search still fails, check the `affine` and `indexer` service logs together.

## 5. Desktop client cannot connect

Check:

- the site is reachable over HTTPS
- the public URL is `https://docs.zacariahheim.com`
- reverse proxy routing points at container port `3010`
- the AFFiNE server external URL matches exactly

Desktop/server connection problems are often just incorrect external URL configuration.

## 6. Mail does not send

Check the mailer values in Coolify against the Authentik service env:

- `MAILER_HOST`
- `MAILER_PORT`
- `MAILER_USER`
- `MAILER_PASSWORD`
- `MAILER_SENDER`

For Gmail, use the app password already configured for Authentik rather than a normal account password.

## 7. Bind-mounted data disappears after redeploy

Confirm the Coolify env still points at the same persistent paths:

- `./storage/postgres`
- `./storage/uploads`
- `./storage/config`
- `./storage/manticore`

Do not casually change these after the stack is initialized.

## 8. Coolify deploy is healthy but the app still fails

Common causes:

- AFFiNE image drift if the tag was changed away from the pinned version
- migration failed but only the app logs were checked
- private key missing or changed unexpectedly
- Authentik app/group configuration incomplete

Check in this order:

1. migration logs
2. app logs
3. indexer health
4. Authentik provider/app/group state
5. exact deployed env values

## 9. `ERR_OSSL_UNSUPPORTED` when loading the private key

This usually means `AFFINE_PRIVATE_KEY` was set to a random string instead of a PEM key.

Fix:

- remove `AFFINE_PRIVATE_KEY` from the deployed env
- keep `./storage/config` mounted persistently
- redeploy so AFFiNE can use the generated `private.key` file in that config directory

Only set `AFFINE_PRIVATE_KEY` manually if you are supplying a real PEM-formatted private key.
