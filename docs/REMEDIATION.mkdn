# Repository audit remediation

This note records changes made on the audit remediation branch.

## Addressed in this branch

- Removed hard-coded credential strings from the Node API source and Kaggle token setup script.
- Kept the chat endpoint explicitly documented as a mock rather than claiming it invokes a model.
- Added input validation, bounded JSON request size, origin allowlisting, upstream timeout handling, and controlled upstream error responses.
- Added a Node package manifest and API regression tests.
- Replaced the invalid root Dockerfile with a Node 22 container for the API.
- Changed GitHub Pages to publish only the reviewed `docs/` directory.
- Replaced the broken Sphinx-style documentation build command with checks matching the repository's existing static documentation.
- Added CI for JavaScript syntax, API tests, and Docker image build.
- Added ignore rules for common local secrets and generated artifacts.

## Required maintainer actions

- Revoke/rotate the previously committed OpenAI service credential and Kaggle token, and inspect their provider-side activity.
- Decide whether to rewrite Git history after coordinating with all collaborators. Current-file cleanup does not remove historical copies.
- Enable GitHub secret scanning and push protection where available.
- Review the provenance, redistribution rights, and necessity of bundled binaries, archives, notebooks, data dumps, and imported code.
- Audit Python, Java, Swift, model-training, and notebook dependencies separately. This branch does not claim those components have been upgraded or tested.
- Review the existing public Pages deployment and check whether sensitive files were previously published.

## Verification scope

The new automated checks are intended to run in GitHub Actions. A passing Node API test suite does not establish that all research notebooks, model training, or other language-specific components work.
