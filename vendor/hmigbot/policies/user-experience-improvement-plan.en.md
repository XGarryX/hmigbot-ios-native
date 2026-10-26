# MigBot User Experience Improvement Plan

The MigBot (迁移精灵) Team (hereinafter "the Team" or "the Operator"), as the operator of the MigBot (迁移精灵) software (hereinafter "the Product"), hereby presents this User Experience Improvement Plan to you (hereinafter "you" or "the User"). This Plan aims to continuously improve AI migration effectiveness and product quality by collecting work-process artifacts generated during migration, providing you with a more stable and efficient experience.

Please read this Plan carefully and in its entirety before deciding whether to participate. Upon consenting to participate, you shall be deemed to have read, understood, and accepted all terms of this Plan. You have the right to withdraw at any time (withdrawing disables the Product's migration functionality); the methods are set forth in **Article 6, Clause 2**.

> **Important: participation in this Plan is a precondition for using the Product (binary).**
> - **Participate** (`telemetry_consent: "granted"`): the Product is **usable** and uploads all of categories (i)–(v) in Article 2.
> - **Decline** (any other state, including `/a2h-privacy deny`, `/a2h-privacy off`, `A2H_TELEMETRY_OFF=1`): the Product's **migration pipeline is disabled** (it refuses to run from `/a2h-spec` onward) and **nothing is uploaded**.
>
> In other words, **declining disables the Product**. Participation is your choice, but if you decline, the Product's migration functionality is unavailable and no data is collected or uploaded. The upload content, purpose, and de-identification are governed by this Plan.

---

**Article 1  Operator and Contact Information**

1.1 Operating entity: The MigBot (迁移精灵) Team

1.2 UX-dedicated email: migbot_uxfeedback@163.com

---

**Article 2  What Participation Involves**

2.1 This Plan does not collect any personal information. 

 **The Product performs no other background collection**; it collects only the following work-process artifacts, and **only while you participate** (`granted`); if you decline, the Product is disabled and collects nothing. When you participate, what is uploaded and when:

-  (i) **lines-of-code statistics** + application names: the Android-side line counts and app name are uploaded when you complete project initialization via `/a2h-init`; the HarmonyOS side is completed at the `a2h-retrospect` stage.
-  (ii) **precise token-usage snapshot**: uploaded per stage as each migration stage (`a2h-init` / `a2h-build` / `a2h-spec` / `a2h-plan` / `a2h-execute` / `a2h-verify` / `a2h-retrospect`) completes.
-  (iii) **build scenario information** and the **migration retrospect report**: uploaded together with the migration artifacts when `/a2h-run` reaches the `a2h-retrospect` stage.

To support the above and to let you request deletion later, the Product generates an **opaque install identifier** (`migbot_session_id`) at `/a2h-init` and sends it with every upload. This identifier contains, and can be reversed to, **no** personal-identity information; it serves only as a deletion handle and for activity de-duplication. Apart from the above, the Product performs no other background collection.

2.2 Work-Process Artifacts Uploaded Upon Participation

The data uploaded by the Product comprises the following five categories and is **strictly limited** to these five categories:

(i) Lines-of-code statistics (`code-lines.json`): lines of code grouped by file extension for the Android and HarmonyOS sides; project name and application name;

(ii) Resource consumption statistics (`usage.json`): per-pipeline-stage token consumption, tool call counts, skill call counts, error counts, and durations;

(iii) Build scenario information (`build-scenario.json`): build exit code, result, problem summary, and error output;

(iv) Migration retrospect report (`docs/retrospect-report-*.md`, bundled with the upload): the migration-quality review report produced by the `a2h-retrospect` stage — skill coverage, compile-error patterns, API corrections, confidence accuracy and other migration-process statistics and reflections; it contains **no** source code, migration intermediate artifacts, or session transcripts.

(v) Precise token-usage snapshot (`usage-v2/<session>.json`): per-skill and per-sub-agent token counts (input / output / cache), broken down by model, for a migration session — skill and sub-agent names and token counts **only**, with no source code, prompts, or message content. This snapshot is captured **locally only** by the hooks at the end of each session turn, and uploaded **per stage** as each migration stage completes (no longer uploaded in real time every turn, to reduce upload frequency).

All five categories are **work-process artifacts** — intermediate files and statistics automatically generated during the migration pipeline, not user personal data.

---

**Article 3  Purpose of Work-Process Artifact Use**

The Team collects the work-process artifacts set forth in Article 2 **solely** for the following purposes:

(i) Evaluating and improving AI migration effectiveness, identifying frequently failing code patterns, and expanding the skill knowledge base;

(ii) Reproducing and fixing product defects (bugs) reported by users;

(iii) Monitoring product health, including error rates and performance bottlenecks.

---

**Article 4  De-identification**

4.1 The Product sanitises data twice: once before it leaves your machine, and once before persistence on the server side.

4.2 Client-side sanitisation: local absolute paths (e.g. `/Users/<your-username>/`, `C:\Users\<your-username>\`) are stripped and replaced with `~`; git committer emails are stripped; no identity fields are collected.

4.3 Server-side sanitisation: only project-level identifiers (project name, application name) are persisted; the source IP is not written to business storage (it is consulted only by the rate-limit and blocklist subsystem on a 10-minute rolling window, then discarded, physically isolated from business data); no field linkable to a natural person is retained.

4.4 Data processed pursuant to the preceding two clauses **cannot** be reverse-attributed to any specific natural person.

---

**Article 5  Data Storage and Security**

5.1 Storage Location

All work-process artifacts collected by the Product are stored on servers physically located within the mainland of the People's Republic of China. Data is encrypted end-to-end (SSL/TLS) during transit; the server side likewise applies corresponding security encryption and storage-protection measures, with SHA-256 integrity verification on every file.

5.2 Encryption and Anti-leak Measures

(i) Data transport uses HTTPS, with TLS terminated at the Nginx front door;

(ii) All operations actions (data export, deletion, blocklist changes) are recorded in an audit log.

5.3 Access Control

Only **operators and core engineering staff** of the Team may access raw data. All access actions are recorded in the audit log and are fully traceable.

5.4 Retention Periods

(i) Raw data (including the migration retrospect report and detailed metrics): retained for **no longer than 12 months**; purged or anonymously aggregated by background tasks upon expiry;

(ii) Anonymised aggregated statistics (weekly/monthly aggregates of lines of code, token consumption trends, etc., containing no original text): may be retained long-term, used solely for product trend analysis, containing no fields linkable to a specific project;

(iii) Upon your withdrawal from this Plan: the Team shall delete, within **30 business days** of receipt of your withdrawal, all raw data linkable to your local project (matched by project name); anonymised aggregated statistics already produced are not subject to deletion as they cannot be reverse-attributed.

5.5 Should you require a shorter retention period or expedited deletion, please contact the Team via the methods set forth in **Article 8**.

---

**Article 6  Your Rights**

6.1 Right of Access and Copy

Your local `.migbot/metrics/<project>/` directory retains a complete copy of every uploaded artifact (`summary.json` and `spec-<upload_id>.tar.gz`). You may inspect them at any time:

```
ls .migbot/metrics/
cat .migbot/metrics/<project>/summary.json
tar -tzf .migbot/metrics/<project>/spec-*.tar.gz
```

If the Team has deployed the MigBot (迁移精灵) data dashboard service, you may log in to inspect all upload records related to your projects and export the raw data.

6.2 Right to Withdraw

You may withdraw at any time. **Withdrawing disables the Product's migration functionality** and uploads nothing thereafter:

(i) Execute `/a2h-privacy deny` (or `/a2h-privacy off`), or manually change `"telemetry_consent"` in `.migbot/config.json` to `"denied"` (or `"off"`). The change takes effect immediately upon save.

(ii) **One-shot withdrawal**: before running a command, set the environment variable `A2H_TELEMETRY_OFF=1` (effective only for the current process; does not modify persistent configuration).

To use the Product again after withdrawing, re-participate per Article 6, Clause 4.

6.3 Right of Deletion

The preceding methods only stop future uploads. To request deletion of historical data already uploaded to the server, please submit a deletion request to the Team via the contact methods in **Article 8**. The Team shall process such requests within 7 business days of receipt.

6.4 Right to Re-participate

You may re-join this Plan at any time by executing `/a2h-privacy accept` or by reverting the `telemetry_consent` field in the configuration to `"granted"`.

6.5 Right to Query Status

You may query the current participation state and the timestamp of the last change via `/a2h-privacy status`.

---

**Article 7  Plan Changes**

7.1 This Plan takes **effect** on 5 June 2026.

7.2 This Plan ships with each MigBot (迁移精灵) client release. The currently effective version always resides at `.migbot/policies/user-experience-improvement-plan.en.md` within the installed client.

7.3 When this Plan undergoes a **material change** (including but not limited to: new work-process artifact categories collected, changed collection purposes, changed storage location, changed operating entity), the new client version shall **re-request** your consent during the `/a2h-init` flow; your prior consent shall automatically become void.

7.4 Non-material changes (including but not limited to: wording revisions, typo fixes, formatting adjustments) shall not trigger re-consent.

---

**Article 8  Contact Information and Dispute Resolution**

8.1 Contact Information

UX-dedicated email: migbot_uxfeedback@163.com

The Team shall respond within 7 business days of receipt of your feedback.

8.2 Dispute Resolution

Any dispute arising from or in connection with this Plan shall first be resolved through friendly negotiation between the parties; if negotiation fails, either party may bring suit in a competent People's Court.

The conclusion, validity, interpretation, performance, and dispute resolution of this Plan shall be governed by the laws of the People's Republic of China.

---

**Article 9  Supplementary Provisions**

9.1 Your participation is entirely voluntary. However, note that **participation in this Plan is a precondition for using MigBot (迁移精灵)'s migration functionality** — if you decline or withdraw, the Product's migration pipeline (from `/a2h-spec` onward) is disabled and no data is collected or uploaded. You may re-participate at any time via `/a2h-privacy accept` to enable the Product.

9.2 This Plan becomes effective for you upon your explicit expression of consent in the `/a2h-init` flow.

9.3 The Chinese and English versions of this Plan have equal effect; in case of discrepancy, the Chinese version shall prevail.

9.4 If any portion of any clause of this Plan is deemed invalid or unenforceable, the validity of the remaining portions shall not be affected.

9.5 Matters not covered herein shall be handled in accordance with the Personal Information Protection Law of the People's Republic of China, the Data Security Law of the People's Republic of China, the Cybersecurity Law of the People's Republic of China, and other relevant laws and regulations.

---

Version: v2.1.1

Effective: 5 June 2026