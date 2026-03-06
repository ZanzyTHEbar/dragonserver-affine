# AFFiNE Deployment (Coolify + Authentik OIDC)

AFFiNE is deployed as a Coolify Docker Compose application at `https://docs.zacariahheim.com`.

This stack is based on the official AFFiNE self-hosted compose, with the server-side indexer enabled from day one and adjusted for Coolify's standard Docker Compose mode.

## Stack

- **AFFiNE**: `ghcr.io/toeverything/affine@sha256:638893c8f62bb7fd0b3028863096f2b057e3c7ca2ac5163574c333698a331f33`
- **Migration job**: same AFFiNE image, one-shot predeploy job
- **PostgreSQL**: `pgvector/pgvector:pg16`
- **Redis**: `redis:7.4-alpine`
- **Indexer**: `manticoresearch/manticore:10.1.0`
- **Public URL**: `https://docs.zacariahheim.com`
- **OIDC provider**: Authentik (`https://auth.zacariahheim.com`)

## Compose File

Use [docker-compose.yaml](docker-compose.yaml) in this folder.

Important Coolify-specific behavior:

- The compose file is the single source of truth.
- Only the `affine` service should get a public domain in Coolify.
- Do not add manual Traefik labels.
- `affine_migration` uses `exclude_from_hc: true` and `restart: "no"` because it exits successfully after running once.

## Required Environment Variables

Copy [.env.example](.env.example) into your local operator environment and provide real values in Coolify.

### Critical values

- `AFFINE_IMAGE_DIGEST=sha256:638893c8f62bb7fd0b3028863096f2b057e3c7ca2ac5163574c333698a331f33`
- `MANTICORE_VERSION=10.1.0`
- `AFFINE_SERVER_HOST=docs.zacariahheim.com`
- `AFFINE_SERVER_EXTERNAL_URL=https://docs.zacariahheim.com`
- `DB_PASSWORD=<generated-secret>`

### Persistent storage

The compose intentionally uses fixed repo-relative bind mounts because Coolify's Docker Compose app parser rejects variable substitution in volume source paths.

Storage paths are:

- `./storage/postgres`
- `./storage/uploads`
- `./storage/config`
- `./storage/manticore`

Keep those paths stable after initial deployment.

`./storage/config` is especially important: AFFiNE writes its generated PEM private key there on first boot as `private.key`. Do not set `AFFINE_PRIVATE_KEY` to a random string in Coolify unless you are intentionally supplying a valid PEM private key.

### SMTP

Use the SMTP settings already present on the Authentik service:

- `MAILER_HOST=smtp.gmail.com`
- `MAILER_PORT=587`
- `MAILER_USER=<from Authentik env>`
- `MAILER_PASSWORD=<from Authentik env>`
- `MAILER_SENDER=AFFiNE <zacariahheim@gmail.com>`

## Coolify Deployment Flow

1. Create a new Coolify application from this repo/folder using Docker Compose mode.
2. Point Coolify at [docker-compose.yaml](docker-compose.yaml).
3. Set the environment variables from [.env.example](.env.example).
4. Assign the public domain to the `affine` service as:
   - `https://docs.zacariahheim.com:3010`
5. Deploy the stack.

Expected runtime behavior:

- `postgres`, `redis`, and `indexer` stay private.
- `affine_migration` exits after a successful predeploy run.
- `affine` becomes the only externally routed service.

## First Boot

After the stack is healthy:

1. Visit `https://docs.zacariahheim.com/admin`
2. Create the initial AFFiNE admin account
3. Log in to AFFiNE admin settings
4. Configure OIDC against Authentik using the values documented in [AFFINE_AUTHENTIK_SETUP.md](AFFINE_AUTHENTIK_SETUP.md)
5. Configure SMTP in the AFFiNE admin settings if the UI settings should mirror the env-backed mailer values

## Validation Checklist

- AFFiNE home page loads on `https://docs.zacariahheim.com`
- `/admin` is reachable
- OIDC login returns successfully from Authentik
- attachments persist across restart
- server-side search works with the indexer enabled
- SMTP test mail succeeds
- the desktop client can connect to the self-hosted server

## References

- [AFFiNE Docker Compose docs](https://docs.affine.pro/self-host-affine/install/docker-compose-recommend)
- [AFFiNE compose reference](https://docs.affine.pro/self-host-affine/references/docker-compose-yml)
- [AFFiNE indexer docs](https://docs.affine.pro/self-host-affine/administer/indexer)
- [Coolify Docker Compose docs](https://coolify.io/docs/knowledge-base/docker/compose)
