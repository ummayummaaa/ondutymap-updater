# OnDutyMap updater

Public execution kit for https://ondutymap.ioanniskotidism.workers.dev.

`updater.mjs` is the standalone Node 22+ updater bundled from OnDutyMap: it fetches official Greek Ministry of Health PDFs, parses them strictly, imports via authenticated API, then verifies saved rows and PDF SHA-256. It contains no credentials.

`cloud-check.py` independently extracts the original PDFs with pdfplumber and submits a comparison against saved records. Disagreements fail the job and do not rewrite records. Public results: `/api/cloud-audit-status`.

GitHub Actions runs on standard Ubuntu every three hours and supports manual dispatch. UPDATER_TOKEN is stored only as an encrypted Actions secret. No caches or artifact uploads are used. Telegram notifications are not configured on this Cloudflare copy.

For manual execution, provide the updater credential through stdin JSON only. Never commit or print credentials. The Worker accepts only the hash of this credential. PDFs and hospital schedule data remain on Cloudflare D1.
