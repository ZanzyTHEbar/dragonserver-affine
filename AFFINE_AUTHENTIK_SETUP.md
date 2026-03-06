# AFFiNE + Authentik (OIDC) on DragonServer

AFFiNE uses Authentik as its OIDC provider for login at `https://docs.zacariahheim.com`.

This setup follows the same repo conventions as `openwebui` and `mealie`:

- Authentik app slug: `affine`
- Authentik access group: `affine-users`
- public issuer base: `https://auth.zacariahheim.com/application/o/affine/`

## Authentik Objects

### Provider and application

Create:

- **Provider name**: `AFFiNE OIDC`
- **Application name**: `AFFiNE`
- **Application slug**: `affine`
- **Launch URL**: `https://docs.zacariahheim.com`

### Redirect URI

Use this exact redirect URI:

- `https://docs.zacariahheim.com/oauth/callback`

### Scopes

Attach the standard mappings:

- `openid`
- `email`
- `profile`

Without these, downstream userinfo lookups may fail or return incomplete identity data.

## Group Model

### Required gate group

Create:

- `affine-users`

Bind the AFFiNE application to an access policy that requires membership in `affine-users` so only approved users can complete login.

### Bundle inheritance

Update `bundle-standard` to include `affine-users` in its `attributes.child_groups` list.

That keeps AFFiNE aligned with the existing standard-access bundle pattern already used for:

- `mealie-users`
- `openwebui-users`
- `opencloud-users`

## ORM Bootstrap Script

Run [create_authentik_oidc.py](create_authentik_oidc.py) inside the Authentik server container to create or update:

- the AFFiNE provider
- the AFFiNE application
- the `affine-users` group
- the `affine-users-access` expression policy

The script prints:

- `CLIENT_ID`
- `CLIENT_SECRET`
- `APP_SLUG`
- `REDIRECT_URI`
- `GROUP`

## AFFiNE OIDC Values

In AFFiNE admin settings, configure OIDC with:

- **Issuer**: `https://auth.zacariahheim.com/application/o/affine/`
- **Client ID**: value printed by the bootstrap script
- **Client Secret**: value printed by the bootstrap script
- **Callback**: `https://docs.zacariahheim.com/oauth/callback`

## Admin Bootstrap

Do not rely on OIDC alone for the first AFFiNE admin.

Recommended bootstrap order:

1. deploy AFFiNE
2. create the first AFFiNE admin locally at `/admin`
3. configure OIDC in AFFiNE
4. bind Authentik app access to `affine-users`
5. confirm SSO works for a bundle-based user

Once validated, regular users should come through Authentik only.

## Notes

- The Authentik invitation + Google enrollment flow already lands standard users in `bundle-standard`.
- Adding `affine-users` to `bundle-standard` means invited Google users automatically gain AFFiNE access on login.
- AFFiNE's internal admin role remains AFFiNE-managed; Authentik gates access, but it does not replace AFFiNE's own admin bootstrap.
