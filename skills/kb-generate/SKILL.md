---
name: kb-generate
description: Generate or refresh the flow knowledgebase for a target codebase — architecture doc with a Mermaid diagram, module map, conventions, and key files — and ensure OpenSpec is set up in that repo. Use when the user says "build/generate/refresh the knowledgebase for <repo>", "run kb-generate", or before slicing a PRD against a repo that has no knowledgebase yet.
---

# kb-generate

Produces a repeatable, rerunnable knowledgebase for a target repo, stored in this plugin's
`kb/<repo-slug>/` directory (never inside the target repo). Invoke as:

`/kb-generate <target-repo-path>`

## Steps

1. **Resolve the repo slug.**
   - Run `git -C <target-repo-path> remote get-url origin` if it succeeds, derive the slug from
     the remote (basename, strip `.git`, lowercase, replace non `[a-z0-9-]` with `-`).
   - Otherwise use the lowercased, sanitized basename of `<target-repo-path>`.
   - `kb/<slug>/` is this repo's home for the rest of the pipeline.

2. **Check for a rerun short-circuit.** If `kb/<slug>/manifest.json` exists, read its
   `last_crawl_commit` and compare to `git -C <target-repo-path> rev-parse HEAD`. If they match,
   tell the user the knowledgebase is already current and stop — don't regenerate for nothing.

3. **Run the deterministic crawl.**
   ```
   python3 scripts/kb/crawl_repo.py <target-repo-path>
   ```
   This is pure scripting (file tree, language mix, manifests/frameworks, git history, largest
   and most-changed files) — no judgment involved, don't second-guess its output, just use it as
   input to the next step.

4. **Write the four knowledgebase docs** using the templates in `templates/` as the structural
   skeleton (`architecture.md.tmpl`, `module-map.md.tmpl`, `conventions.md.tmpl`,
   `key-files.md.tmpl`) — replace the HTML-comment guidance in each with real content grounded in
   the crawl output plus a sample of the actual key/largest files you read directly. Write the
   results to `kb/<slug>/architecture.md`, `module-map.md`, `conventions.md`, `key-files.md`.
   - **`architecture.md` must include a real Mermaid diagram** (flowchart or C4-style) built from
     the actual crawled module/service structure — real names, not a generic placeholder. This is
     the single most useful artifact for `slice-prd` and `kickoff` to orient against, so don't
     skip it or leave it templated.
   - Only state what's actually observable in the crawl output or the files you read. Don't
     invent conventions or components that aren't there.

5. **Set up OpenSpec in the target repo** (this is where architectural decisions from later
   phases will live, not in `flow`):
   ```
   bash scripts/kb/openspec_setup.sh <target-repo-path>
   ```
   This is idempotent and fails soft — if it warns and exits 0 without creating `openspec/`
   (e.g. no npm, network unavailable), continue anyway; note the warning to the user at the end
   rather than treating it as blocking. Knowledgebase generation must succeed independent of
   OpenSpec's availability.
   - **This leaves `openspec/` and `.claude/skills/openspec-*` as untracked, uncommitted files in
     the target repo** — `flow` doesn't commit into someone else's repo on its own initiative.
     Tell the user this plainly at the end (step 8) and that it's their call whether to commit it,
     gitignore it, or leave it untracked. It also means these files exist only on whatever branch
     is currently checked out — a git worktree created later by `/kickoff` from that same base
     branch will **not** inherit them (worktrees only get committed content), so `/kickoff` runs
     its own per-worktree OpenSpec setup for architectural stories rather than relying on this.

6. **Write/update `kb/<slug>/manifest.json`**:
   ```json
   {
     "target_path": "<absolute target repo path>",
     "git_remote": "<remote url or null>",
     "last_crawl_commit": "<HEAD sha>",
     "last_crawl_date": "<ISO date>"
   }
   ```

7. **Create `kb/<slug>/stories/` if it doesn't exist yet** (empty is fine — `slice-prd` populates
   it later).

8. Report back to the user: what was generated, whether OpenSpec setup succeeded, and where the
   knowledgebase lives (`kb/<slug>/`).
