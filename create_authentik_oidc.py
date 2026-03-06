#!/usr/bin/env python3
"""Run inside the Authentik server container to create the AFFiNE OIDC app/provider and gate group.

This script is idempotent:
- creates or updates the OAuth2 provider
- creates or updates the AFFiNE application
- ensures the `affine-users` group exists
- attaches the standard openid/email/profile scope mappings
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "authentik.root.settings")

import django

django.setup()

from authentik.core.models import Application, Group
from authentik.crypto.models import CertificateKeyPair
from authentik.flows.models import Flow
from authentik.providers.oauth2.models import OAuth2Provider, ScopeMapping

AFFINE_URL = "https://docs.zacariahheim.com"
REDIRECT_URI = f"{AFFINE_URL}/oauth/callback"
APP_SLUG = "affine"
APP_NAME = "AFFiNE"
GROUP_NAME = "affine-users"

auth_flow = Flow.objects.get(slug="default-authentication-flow")
authz_flow = Flow.objects.get(slug="default-provider-authorization-implicit-consent")
inv_flow = Flow.objects.get(slug="default-provider-invalidation-flow")
signing_key = CertificateKeyPair.objects.get(name="authentik Self-signed Certificate")

provider, created = OAuth2Provider.objects.get_or_create(
    name="AFFiNE OIDC",
    defaults={
        "authentication_flow": auth_flow,
        "authorization_flow": authz_flow,
        "invalidation_flow": inv_flow,
        "signing_key": signing_key,
        "encryption_key": None,
        "_redirect_uris": [{"matching_mode": "strict", "url": REDIRECT_URI}],
    },
)

if not created:
    provider.authentication_flow = auth_flow
    provider.authorization_flow = authz_flow
    provider.invalidation_flow = inv_flow
    provider.signing_key = signing_key
    provider.encryption_key = None
    provider._redirect_uris = [{"matching_mode": "strict", "url": REDIRECT_URI}]
    provider.save()

app, app_created = Application.objects.get_or_create(
    slug=APP_SLUG,
    defaults={"name": APP_NAME, "provider": provider, "meta_launch_url": AFFINE_URL},
)

if not app_created:
    app.name = APP_NAME
    app.provider = provider
    app.meta_launch_url = AFFINE_URL
    app.save()

group, group_created = Group.objects.get_or_create(
    name=GROUP_NAME,
    defaults={"attributes": {"description": "Access gate for AFFiNE"}},
)

if not group_created and not group.attributes:
    group.attributes = {"description": "Access gate for AFFiNE"}
    group.save(update_fields=["attributes"])

for scope in ScopeMapping.objects.filter(scope_name__in=["openid", "email", "profile"]):
    provider.property_mappings.add(scope)

print("CLIENT_ID", provider.client_id)
print("CLIENT_SECRET", provider.client_secret)
print("APP_SLUG", app.slug)
print("REDIRECT_URI", REDIRECT_URI)
print("GROUP", group.name)
