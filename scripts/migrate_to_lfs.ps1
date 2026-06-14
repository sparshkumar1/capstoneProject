# PowerShell helper to migrate large tracked files to Git LFS
# Usage: .\scripts\migrate_to_lfs.ps1

param()

Write-Host "Checking for git and git-lfs..."
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git not found in PATH. Install git and retry."
    exit 1
}

$giff = & git lfs version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "git-lfs not found. To install: https://git-lfs.com/"
    Write-Host "You can still remove large files manually (see docs/GIT_LFS_MIGRATION.md)"
    exit 1
}

Write-Host "git-lfs found: migrating configured patterns..."
# Patterns are picked from .gitattributes
# This will rewrite history — ensure you have backed up branches and collaborators are informed.
& git lfs migrate import --include="models/**,services/evaluator/models/**,models/qwen_7b/**,ablation/results/*.npy,ablation/results/*.pt,ablation/results/*.bin,artifacts/**"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration complete. Run 'git push --force origin HEAD' to update remote." 
} else {
    Write-Error "Migration failed. See output above. Consider using 'git lfs install' or the BFG tool." 
}
