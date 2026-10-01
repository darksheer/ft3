## 2026-10-01 - Added TruffleHog Secret Scanning to GitHub Actions
**Vulnerability:** Missing automated secret scanning in CI/CD pipeline.
**Learning:** To proactively protect against hardcoded secrets in the repo, a secret scanning action should be included to scan PRs and pushes.
**Prevention:** Added a TruffleHog GitHub Action workflow.
