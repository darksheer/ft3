## 2025-03-04 - [Added Secret Scanning]
**Vulnerability:** Missing automated secret scanning in CI pipeline.
**Learning:** This is a data-oriented repository (CSV/JSON files representing fraud tactics). These files are updated over time, presenting a risk of accidentally committing API keys or other credentials within large datasets.
**Prevention:** Implement TruffleHog GitHub Action to automatically scan all pull requests and commits for inadvertently exposed verified secrets.
