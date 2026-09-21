# P1 — ICETC double-blind anonymisation checklist (master pass, 2026-09-21)

Legend: ✅ done and checked · ⬜ author action · ❓ not verifiable from the pages read

Upload candidate: `P1_ICETC_BLINDED.pdf` (from `P1_ICETC_BLINDED.docx`). Never upload `P1_ICETC_MASTER_author_identifying.*`.

| # | Item | Status | Evidence / note |
|---|---|---|---|
| 1 | Author names, designation, affiliations removed; "Anonymous authors (double-blind submission)" only | ✅ | blinded PDF page 1; the builder asserts that none of "Uma", "Khadd", "Sparsh", "Athreya", "Manasa", "PES University", "pes.edu" occurs in the blinded source |
| 2 | Extracted PDF text scanned for author names, institution, e-mail domains, product name and the word "acknowledg" | ✅ | 0 hits on the final build (`audit_v2/pdf_qa_check.py --mode blinded`: whole-word scan of the rendered text, the metadata and XMP, and the raw file bytes, plus a check for personal Windows paths); the rendered pages were also inspected by eye (`P1_VISUAL_QA_REPORT.md`) |
| 3 | Acknowledgments | ✅ removed | the blinded copy has no acknowledgments section; see item 12 for the AI-use disclosure question |
| 4 | Repository URL, account or host names in text, captions, tables, figure | ✅ | none; the only URL is the public Docker documentation reference [14] |
| 5 | Product name of the system | ✅ | the sandbox image name was replaced by "the project's local sandbox image"; the manuscript already uses "the pipeline" and "the system under test" |
| 6 | Self-citations | ✅ none | no reference is a project or author paper |
| 7 | DOCX metadata | ✅ | `docProps/core.xml`: creator "Anonymous", last-modified-by empty; the template's original creator strings were removed; no author string in any DOCX part |
| 8 | PDF metadata | ✅ | no /Author, /Title, /Subject or /Keywords entry; the XMP block has only the producer (Microsoft Word), dates and a document UUID |
| 9 | Title page, headers, footers, captions, tables | ✅ | inspected in the rendered pages; the template's first-page footer is empty |
| 10 | Git tags and short commit hashes in the blinded text (`release/app-repair/v1`, `sut/X1/build-A/B`, `980747ff`, `beb374f3`) | ⬜ decision | **Finding:** the cited commits and the `release/...` and `sut/X1/...` tags are **not on any remote branch or remote tag** at present (`git branch -r --contains`, `git ls-remote --tags origin`); the remote is `github.com/sparshkumar1/capstoneProject` (the account name is in the URL), and the branch is 33 commits ahead of it. Today the identifiers do not resolve publicly. If those commits or tags are pushed, or the repository is public and later updated, a reviewer could locate the repository from them. The repository's visibility could not be checked here (UNVERIFIED). They are kept because the baseline/repaired SUT definition depends on them; the paper's own naming ("baseline SUT / repaired SUT") would still stand without them. **Do not push the branch or tags while the paper is under review, or replace the identifiers in the blinded copy** |
| 11 | Template's "Authors' background" page | ⬜ decision | not included. The official pages read do not say it is required at submission; whether ICETC wants it, and how it is kept from reviewers, is unresolved |
| 12 | AI-use disclosure in a blinded manuscript | ⬜ policy question | IEEE's policy places the disclosure in the acknowledgments for IEEE-published proceedings; ICETC's own rule was not found on the pages read. The blinded copy therefore carries no disclosure text (it would not identify the authors, but its facts are unconfirmed). The body still states, as a method fact, that one AI coding agent designed, ran, repaired and re-tested the X1 campaigns, because the independence of the re-test depends on it. Ask the organisers whether a disclosure is required at review time; add it after the authors confirm the facts (`cross/AI_DISCLOSURE_FACT_CHECK.md`) |
| 13 | Preprint or web posting during review | ⬜ | do not post; ICETC's rule is not stated (UNVERIFIED) |
| 14 | Blind-review requirement itself | ✅/❓ | double-blind stated on `cfp.html`; absent from the EasyChair CFP |
| 15 | File properties after any re-export | ⬜ | re-check the PDF properties whenever the file is regenerated |
| 16 | The build folder | ⬜ | `build_icetc_docx.py` and the master files contain the author names; upload only the single blinded PDF, not this folder |
