# Security Policy

## Credentials

Never commit API keys, access tokens, passwords, private keys, or populated environment files. Supply runtime credentials through environment variables or an approved secret manager. Keep local credential files owner-readable only.

If a credential is committed, assume it is compromised:
1. Revoke or rotate it at the issuing provider immediately.
2. Review provider audit logs, usage, and billing.
3. Remove the credential from the current source tree.
4. Assess whether history rewriting is warranted; coordinate it with collaborators because it changes commit IDs.
5. Enable GitHub secret scanning and push protection where available.

Removing a secret from the latest commit does not invalidate it or remove it from Git history, forks, caches, or clones.

## Reporting

Please report security issues privately to the repository maintainers rather than opening a public issue containing exploit details or credentials.
