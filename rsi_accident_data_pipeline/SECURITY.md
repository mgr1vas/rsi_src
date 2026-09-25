# Security

## Secrets

Never commit or paste into issues/PRs:
- `SUPABASE_SECRET_KEY`
- legacy Supabase `service_role` keys
- database passwords
- API tokens

The Supabase secret key belongs only on controlled developer/server machines.
It must never be included in Flutter or other shipped client code.

If a secret is committed accidentally, revoke/rotate it immediately in Supabase.
