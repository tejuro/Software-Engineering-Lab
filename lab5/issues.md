# Lab 05 — Static Code Analysis: Issues and Fixes

**File analysed:** `fare_calculator.py`  
**Tools:** Pylint, Bandit, Flake8

The line references below refer to the original version or the relevant code section; line numbers may differ in the final file.

| Issue | Type / Tool | Description | Fix applied |
|---|---|---|---|
| Unused `os` import | Code quality — Pylint / Flake8 | An imported module was not used. | Removed the unused import. |
| Lambda assigned to a variable | Code quality — Pylint / Flake8 | `baseOf = lambda km: fareForDistance(km)` made the code less clear and triggered a style warning. | Replaced it with a named function, `base_of()`. |
| Missing docstrings and non-snake_case names | Code quality — Pylint | Several functions and the module lacked documentation and used inconsistent naming. | Added docstrings and renamed functions to snake_case. The XML callback `startElement` retains the name expected by the SAX API. |
| Mutable default argument | Potential bug — Pylint | `categories=[]` used a mutable object as a default argument. | Changed the default to `None` and created a list inside the function when needed. |
| Daily cap was not applied to the total | Logic bug | The original code changed a loop variable but returned the uncapped total. | Calculated the total and returned the smaller of the total and `DAILY_CAP`. |
| Card balance could become negative | Logic bug | A journey was charged even when the card did not have enough money. | Added a balance check and reject the trip when the balance is insufficient. |
| Floating-point money values | Reliability — code quality | Binary floating-point arithmetic can produce values such as `0.30000000000000004`. | Used `Decimal` for fare and balance calculations. |
| MD5 checksum | Security — Bandit B303 | MD5 is not suitable where a stronger modern hash is required. | Replaced MD5 with SHA-256. The checksum is used for integrity identification, not as a digital signature. |
| XML parser security | Security — Bandit B406 / B317 | Standard-library SAX parsing of untrusted XML can be unsafe. | Used `defusedxml` parsing and enabled `defuse_stdlib()`. The remaining B406 import warning is suppressed with a targeted `# nosec B406` comment because the handler interface is still imported from `xml.sax.handler`. This suppression hides the scanner finding; it is not itself a security fix. |
| Automatic SSH host-key acceptance | Security — Bandit B507 | `AutoAddPolicy()` trusted unknown SSH host keys automatically. | Loaded system host keys and used `RejectPolicy()` to reject unknown hosts. |
| Remote shell command injection risk | Security — Bandit B601 | Building a remote shell command using a file path can expose command-injection risk. | Removed `exec_command()` and changed the function to upload the file with SFTP. The remote gate must be configured to process the uploaded file; this changes the original remote-install workflow. |
| Hardcoded temporary directory | Security — Bandit B108 | A fixed `/tmp/...` path was flagged. | Changed the upload destination to a relative filename in the SFTP account's starting directory. Confirm the gate is configured to process the file there. |
| Formatting and line-length issues | Style — Flake8 | The original file had blank-line, line-length, and lambda-style violations. | Reorganized imports and spacing, wrapped long lines, and used a named function. |

## Final verification

- **Pylint:** final reported score was **10.00/10**.
- **Flake8:** final check produced no output, indicating no reported style violations.
- **Bandit:** the final report showed no unsuppressed issues. One B406 finding is suppressed using `# nosec B406`; therefore, the report should not be described as proof that every finding was independently eliminated.

