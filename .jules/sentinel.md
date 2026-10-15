## 2024-10-15 - Add TruffleHog Secret Scanning
**Vulnerability:** The repository lacked automated secret scanning, meaning hardcoded secrets could be inadvertently committed and exposed.
**Learning:** Adding a CI/CD workflow like TruffleHog provides an automated layer of defense in depth to catch secrets before they are merged.
**Prevention:** Always ensure automated secret scanning is implemented in repositories, especially those with configuration or data files, to prevent accidental secret leakage.
