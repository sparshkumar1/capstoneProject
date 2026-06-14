Git LFS migration and push-fix guide

Problem: A recent `git push` failed due to very large objects (model files, FAISS indices, etc.). The following steps help migrate large tracked files to Git LFS and clean the local branch so a push will succeed.

Prerequisites
- git installed
- git-lfs installed and configured (`git lfs install`)
- Make sure your working tree is clean and you've committed any intended changes.

Quick steps (recommended)
1. Install git-lfs:

```powershell
# Windows (PowerShell)
choco install git-lfs -y
git lfs install
```

2. Run the helper migration script (rewrites history):

```powershell
.\scripts\migrate_to_lfs.ps1
```

3. Force-push the current branch to update remote history (ONLY after coordinating with collaborators):

```powershell
git push --force origin HEAD
```

Notes
- The migration rewrites history for the branch and moves matching files to LFS. This reduces pack size and allows pushes to succeed. If you prefer a safer manual route, remove large files from the index, add them to `.gitignore`, commit, and push.

Manual fallback (no git-lfs)
1. Identify large tracked files:

```powershell
# show largest objects
git rev-list --objects --all | 
  ForEach-Object { $_ } | 
  # use git verify-pack or external tools to identify large blobs (see Git docs)
```

2. Remove large files from the index (keep local copy):

```powershell
git rm --cached path/to/large_file
# commit and push
git commit -m "chore: remove large artifact from repo"
git push origin HEAD
```

3. Add the path to `.gitignore` and upload large models to a release or external storage (Zenodo, OSF, S3).

If you need help identifying which files to remove, run `git status --porcelain` and `git ls-files -s` and contact me; I can generate a candidate list and patch `.gitignore` for you.
