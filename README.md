# OnDutyMap updater

Public execution kit for https://ondutymap.ioanniskotidism.workers.dev.

`updater.mjs` is the standalone Node 22+ updater bundled from OnDutyMap: it fetches official Greek Ministry of Health PDFs, parses them strictly, imports via authenticated API, then verifies saved rows and PDF SHA-256. It contains no credentials.

`cloud-check.py` independently extracts the original PDFs with pdfplumber and submits a comparison against saved records. Disagreements fail the job and do not rewrite records. Public results: `/api/cloud-audit-status`.

GitHub Actions runs on standard Ubuntu every three hours and supports manual dispatch. UPDATER_TOKEN is stored only as an encrypted Actions secret. No caches or artifact uploads are used. Telegram notifications are not configured on this Cloudflare copy.

For manual execution, provide the updater credential through stdin JSON only. Never commit or print credentials. The Worker accepts only the hash of this credential. PDFs and hospital schedule data remain on Cloudflare D1.

### Automatic recovery (16 November 2026)

The existing workflow runs every twenty minutes and retries the original updater at most three times. It keeps a failing status when any published source cannot be processed. A fresh source manifest may still contain independently matched required dates, with the unresolved future original explicitly in `blockedDays`; this is not an all-days approval. Both Sites transports preserve the blocked date instead of treating it as unpublished. Expiry and exact comparison remain strict.

The November 17 original contains an unresolved numeric obstetrics cell. Both parsers must reject it; the fixture and tests prevent silent omission. Run `python -m unittest discover -s tests`.

If the mutable raw GitHub URL serves expired metadata, readers fall back to the same repository's public Contents API. Both paths retain the original timestamp and strict expiry; Python pins one manifest per independent run. The restricted-network test accepts an explicitly blocked future source only while both required dates are independently extracted with zero direct Ministry requests; it does not turn the overall audit green.
