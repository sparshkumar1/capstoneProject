import os
from pathlib import Path

repo_root = Path(".").resolve()

doc_exts = {".md", ".txt", ".pdf", ".docx", ".doc", ".rst"}
inventory = []

# Known duplicate pairs or superseded documents
def analyze_file(rel_str, name, ext, size):
    lower_path = rel_str.lower().replace("\\", "/")
    
    # Defaults
    category = "General"
    status = "Current"
    authority = "Non-Authoritative"
    uniqueness = "Unique"
    scope = "Shared"
    safe_archive = False
    safe_delete = False
    reason = ""

    # Source code directory readmes or metadata (MUST NOT BE MODIFIED OR DELETED)
    if any(lower_path.startswith(x) for x in ["apps/", "agents/", "services/", "rl/", "data/", "tests/"]):
        category = "Source Code Metadata"
        status = "Current"
        authority = "Level 1 Source of Truth"
        safe_archive = False
        safe_delete = False
        reason = "Source code directory documentation; protected under safety rule."
        return {
            "path": rel_str, "filename": name, "type": ext, "purpose": category,
            "status": status, "authority": authority, "uniqueness": uniqueness,
            "scope": scope, "safe_archive": safe_archive, "safe_delete": safe_delete, "reason": reason
        }

    # Root files
    if "/" not in lower_path:
        if name == "README.md":
            category = "Repository Main README"
            status = "Current"
            authority = "Authoritative"
            reason = "Top-level repo overview."
        elif name == "CHANGELOG.md":
            category = "Project History"
            status = "Historical"
            authority = "Non-Authoritative"
            safe_archive = True
            reason = "Initial commit changelog."
        elif name == "INTERVIEW_PREPARATION_GUIDE.md":
            category = "Candidate / Study Guide"
            status = "Historical / Educational"
            authority = "Non-Authoritative"
            safe_archive = True
            reason = "Comprehensive DSA conceptual guide, not a paper or system doc."
        elif name.endswith(".pdf"):
            category = "Old Manuscript Build"
            status = "Superseded"
            authority = "Non-Authoritative"
            safe_archive = True
            reason = "Compiled IEEE Access draft PDF containing superseded results."
        else:
            category = "Root Documentation"
            status = "Current"
            authority = "Non-Authoritative"
            reason = "Root document."

    # Submission folder (Old drafts and stage audits)
    elif lower_path.startswith("submission/"):
        category = "Historical Submission Package"
        status = "Superseded / Historical"
        authority = "Non-Authoritative (Level 4)"
        scope = "Paper 1 / IEEE Access (Old)"
        safe_archive = True
        if "paper_draft_ieee.md" in lower_path and os.path.exists("submission/manuscript/IEEE_TLT_MANUSCRIPT.md"):
            # Check if duplicate
            p1 = repo_root / "submission" / "manuscript" / "IEEE_TLT_MANUSCRIPT.md"
            p2 = repo_root / "submission" / "manuscript" / "paper_draft_ieee.md"
            if p1.exists() and p2.exists() and p1.stat().st_size == p2.stat().st_size:
                uniqueness = "Exact Duplicate"
                safe_delete = True
                reason = "Exact duplicate of IEEE_TLT_MANUSCRIPT.md."
            else:
                reason = "Historical draft for IEEE Access / TLT."
        else:
            reason = "Old submission bundle for previous conference cycle."

    # Docs folder (Legacy stage reports, checklists, early notes)
    elif lower_path.startswith("docs/"):
        if "stage" in lower_path or "freeze" in lower_path or "gate" in lower_path or "audit" in lower_path:
            category = "Historical Development Stage Report"
            status = "Historical (Level 4)"
            authority = "Non-Authoritative"
            safe_archive = True
            reason = "Historical record of engineering milestones (Stages 11-26)."
        elif "paper_draft" in lower_path or "ieee" in lower_path:
            category = "Historical Paper Draft"
            status = "Superseded (Level 4)"
            authority = "Non-Authoritative"
            safe_archive = True
            reason = "Pre-split monolithic draft for IEEE Access/ToE with ungrounded historical claims."
        elif name in ["PREPAIRED_COMPLETE_BOOKLET.md", "PREPAIRED_HOLY_GRAIL.md"]:
            category = "Consolidated Notes / Historical Booklet"
            status = "Historical (Level 4)"
            authority = "Non-Authoritative"
            safe_archive = True
            reason = "Comprehensive legacy reference manual."
        else:
            category = "Subsystem Technical Documentation"
            status = "Current / Reference"
            authority = "Non-Authoritative (Level 3/4)"
            safe_archive = True
            reason = "Architecture / deployment reference docs."

    # Research folder
    elif lower_path.startswith("research/"):
        if lower_path.startswith("research/audit/"):
            category = "Research Forensic Audit"
            if name in ["claim_audit.md", "current_test_manifest.md", "equation_code_audit.md", 
                        "dataset_inventory.md", "data_leakage_report.md", "failure_matrix.md",
                        "historical_results_reconciliation.md", "paper_overlap_matrix.md", 
                        "privacy_data_flow.md", "threat_model.md", "rl_state_alignment.md",
                        "speech_ethics.md", "reviewer_simulation.md", "current_implementation_map.md"]:
                status = "Current"
                authority = "Authoritative (Level 3)"
                reason = "Current forensic audit verifying implementation truth."
            else:
                status = "Historical Audit"
                authority = "Non-Authoritative"
                safe_archive = True
                reason = "Earlier iteration audit report."

        elif lower_path.startswith("research/papers/"):
            if any(x in lower_path for x in ["paper1/", "paper2/", "paper3/"]):
                category = "Active Paper Manuscript Package"
                status = "Current"
                authority = "Authoritative (Level 3)"
                scope = "Paper Specific"
                reason = "Authoritative canonical paper package."
            else:
                category = "Superseded Paper Draft"
                status = "Superseded (Level 4)"
                authority = "Non-Authoritative"
                safe_archive = True
                reason = "Earlier draft created before formal 3-paper target separation."

        elif lower_path.startswith("research/reproducibility/"):
            category = "Reproducibility Guide"
            status = "Current"
            authority = "Authoritative (Level 2/3)"
            reason = "Step-by-step reproduction instructions."

        elif lower_path.startswith("research/annotation/"):
            category = "Human Annotation Asset"
            status = "Current"
            authority = "Authoritative (Level 2/3)"
            reason = "Standardized human grading rubric and template."

        elif lower_path.startswith("research/tables/"):
            category = "Experimental Result Table"
            status = "Current"
            authority = "Authoritative (Level 2)"
            reason = "Directly generated markdown result table from experiment scripts."

        elif lower_path.startswith("research/capstone/"):
            category = "Academic Capstone Submission"
            status = "Historical"
            authority = "Non-Authoritative"
            safe_archive = True
            reason = "Course capstone reports and rubrics."

        elif lower_path.startswith("research/results/summaries/"):
            category = "Historical Experiment Summary"
            status = "Superseded"
            authority = "Non-Authoritative"
            safe_archive = True
            reason = "Early experiment summaries superseded by research/tables/."

        elif name in ["README.md", "PLAN.md"]:
            category = "Research Master Guide"
            status = "Current"
            authority = "Authoritative (Level 3)"
            reason = "Primary research landing and plan file."

    return {
        "path": rel_str, "filename": name, "type": ext, "purpose": category,
        "status": status, "authority": authority, "uniqueness": uniqueness,
        "scope": scope, "safe_archive": safe_archive, "safe_delete": safe_delete, "reason": reason
    }

for p in repo_root.rglob("*"):
    if not p.is_file():
        continue
    parts = p.parts
    if any(x in parts for x in [".git", ".venv", "node_modules", "__pycache__", ".system_generated"]):
        continue
    if p.suffix.lower() in doc_exts:
        rel = p.relative_to(repo_root)
        inventory.append(analyze_file(str(rel), p.name, p.suffix.lower(), p.stat().st_size))

# Write documentation_inventory.md
os.makedirs("research/audit", exist_ok=True)
out_file = "research/audit/documentation_inventory.md"
with open(out_file, "w", encoding="utf-8") as f:
    f.write("# Complete Repository Documentation & Information Inventory\n\n")
    f.write(f"Total documentation files inspected: **{len(inventory)}**\n\n")
    f.write("### Source-of-Truth Hierarchy Summary\n")
    f.write("- **Level 1 (Absolute Truth):** Production implementation source code and configs\n")
    f.write("- **Level 2 (Experimental Truth):** Raw outputs, checkpoints, scripts, and verified result tables\n")
    f.write("- **Level 3 (Current Canonical Docs):** Verified audits, canonical truth, reproducibility guides, and active paper READMEs\n")
    f.write("- **Level 4 (Historical / Superseded):** Old stage reports, legacy drafts, superseded numbers, previous course submissions\n")
    f.write("- **Level 5 (Duplicates / Junk):** Exact duplicates or redundant copies\n\n")
    f.write("---\n\n")
    f.write("| Path | Type | Purpose | Status | Authority | Unique? | Archive? | Delete? | Reason |\n")
    f.write("| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |\n")
    
    for item in sorted(inventory, key=lambda x: x["path"]):
        f.write(f"| `{item['path']}` | {item['type']} | {item['purpose']} | {item['status']} | {item['authority']} | {item['uniqueness']} | {'YES' if item['safe_archive'] else 'NO'} | {'YES' if item['safe_delete'] else 'NO'} | {item['reason']} |\n")

print(f"Generated {out_file} with {len(inventory)} entries.")
