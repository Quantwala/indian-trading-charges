# Maintainer publishing

The public repository is https://github.com/Quantwala/indian-trading-charges. Source is maintained in the shared Quantwala main checkout under `oss/indian-trading-charges`; do not copy private app files into the public repository.

## Synchronize source

From the existing Quantwala workspace, after tests pass and changes are committed to main:

```powershell
$chargesCommit = git subtree split --prefix=oss/indian-trading-charges
git push https://github.com/Quantwala/indian-trading-charges.git "${chargesCommit}:refs/heads/main"
```

Keep rates synchronized with the app's `source/bhav/src/bhav/costs/india_equity.py` and run the app parity test. The public repository contains library-only history produced by the subtree export.

## PyPI trusted publisher

One-time configuration in the maintainer's PyPI account:

- Project: `indian-trading-charges`
- GitHub owner: `Quantwala`
- Repository: `indian-trading-charges`
- Workflow: `publish.yml`
- Environment: `pypi`

The GitHub release workflow builds and validates distributions, then publishes using OIDC. No PyPI API token is stored in GitHub. The pending publisher creates the project on the first successful upload.

## Release

Update the version and changelog before each new release. Synchronize the public repository, wait for the tests workflow, then publish a GitHub release tagged with that version (for example `v0.1.0`). The publish workflow uploads to PyPI. Verify the public project, install the exact published version in isolation and run the documented examples. PyPI release files cannot be overwritten; correct a defective release with a new version.
