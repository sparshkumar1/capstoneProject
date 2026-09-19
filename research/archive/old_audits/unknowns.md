# ARCHIVED / SUPERSEDED — NOT A SOURCE OF CURRENT FACTS
> **Superseded by:** Current audits in 
esearch/audit/ and 
esearch/CANONICAL_SCIENTIFIC_TRUTH.md  
> **Date Archived:** 2026-09-17  
> **Reason:** Early exploratory audit report superseded by consolidated forensic audits. Preserved for historical record.  

---

# Unknowns, Unverified Claims, and Incomplete Evidence Inventory

**Standard:** Explicit identification of claims where empirical evidence is currently missing from the repository.

---

1. **Longitudinal Learning Retention: UNKNOWN**
   - *Claim:* "PrepAIred improves student technical interview learning retention over time."
   - *Status:* **UNKNOWN — repository evidence insufficient.**
   - *Required Data:* Multi-week controlled trial with pre-test and post-test assessments comparing cohorts using PrepAIred versus static practice. Currently, only cross-session persistent storage exists in SQLite; no human retention data exists.

2. **Full Multi-Rater Human Agreement on Scaled Question Bank: INSUFFICIENT EVIDENCE**
   - *Claim:* "Inter-rater reliability $\alpha = 0.8255$ across all CS interview topics."
   - *Status:* **INSUFFICIENT EVIDENCE.**
   - *Required Data:* The pilot benchmark is restricted to $N=20$ curated answers across 4 topics, with 1 real human rater blended with synthetic proxies. Scaling to 3+ independent human annotators across all 100 questions is required to claim universal human agreement.

3. **Demographic Speech Fairness: UNKNOWN**
   - *Claim:* "Acoustic hesitation scoring is fair across diverse cultural and linguistic backgrounds."
   - *Status:* **UNKNOWN — repository evidence insufficient.**
   - *Required Data:* Acoustic recordings annotated with demographic, accent, and speaker native-language metadata to assess disparate impact.

4. **MicroVM Hardware Boundary Security: UNVERIFIED**
   - *Claim:* "Code execution sandbox is completely impervious to zero-day kernel escapes."
   - *Status:* **UNVERIFIED.**
   - *Reality:* Docker containers share the host Linux kernel. While capabilities are dropped and namespaces isolated, kernel exploits (e.g. privilege escalation syscall bugs) remain a theoretical attack surface.
