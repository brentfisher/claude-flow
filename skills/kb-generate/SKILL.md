---
name: kb-generate
description: Generate or refresh the flow knowledgebase for a target codebase — architecture doc with a Mermaid diagram, module map, conventions, and key files — and ensure OpenSpec is set up in that repo. Use when the user says "build/generate/refresh the knowledgebase for <repo>", "run kb-generate", or before slicing a PRD against a repo that has no knowledgebase yet.
---

# kb-generate

Produces a repeatable, rerunnable knowledgebase for a target repo. **The knowledgebase's real
home is inside the target repo**, at `<target-repo-path>/docs/kb/` — git-tracked alongside the
code it describes, not an orphaned copy that can drift out of sync with it. This plugin's own
`kb/<slug>/` is kept as a **symlink** to that path, never a real directory: every other skill in
this plugin (`slice-prd`, `kickoff`, `open-prs`) reads and writes `kb/<slug>/...` paths, and the
symlink means those keep resolving unchanged while the actual bytes live in, and travel with, the
target repo. It also makes `kb/` here a single directory you can search across every repo flow
tracks (`ls kb/*/`, `grep -r ... kb/`) without walking out to each repo individually — the reason
to keep a central pointer at all, instead of nothing.

Invoke as: `/kb-generate <target-repo-path>`

## Steps

1. **Resolve the repo slug.**
   - Run `git -C <target-repo-path> remote get-url origin` if it succeeds, derive the slug from
     the remote (basename, strip `.git`, lowercase, replace non `[a-z0-9-]` with `-`).
   - Otherwise use the lowercased, sanitized basename of `<target-repo-path>`.

1a. **Ensure `kb/<slug>` is a symlink into the target repo**, before touching anything else:
   - If `kb/<slug>` doesn't exist: `mkdir -p <target-repo-path>/docs/kb/stories`, then
     `ln -s <target-repo-path>/docs/kb kb/<slug>`.
   - If `kb/<slug>` already exists and is a symlink resolving to
     `<target-repo-path>/docs/kb` — continue, nothing to do.
   - If `kb/<slug>` exists as a **real directory** (predates this convention, or was made before
     a repo adopted an in-repo kb of its own): **stop, don't silently migrate or delete it.**
     Compare its `manifest.json` against `<target-repo-path>/docs/kb/manifest.json` if the latter
     exists, and tell the user plainly: which one looks current, whether they've diverged, and
     that reconciling (pick one, `rm -rf` or symlink the other) is their call, not something to
     do on their behalf mid-run.
   - If `kb/<slug>` is a symlink pointing anywhere else (a moved or renamed target repo): stop and
     flag the stale target rather than silently repointing it.

2. **Check for a rerun short-circuit.** If `kb/<slug>/manifest.json` exists (reading through the
   symlink), read its `last_crawl_commit` and compare to
   `git -C <target-repo-path> rev-parse HEAD`. If they match, tell the user the knowledgebase is
   already current and stop — don't regenerate for nothing.

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
   - Each template carries an [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format)
     (Open Knowledge Format) frontmatter block. Fill `description` with a real one-sentence
     summary, `generated.at` with the current UTC ISO 8601 datetime, and the `sources` entry's
     `resource`/`title` with the target repo's git remote and `<repo> @ <HEAD sha>`. Use
     `generated.by: kb-generate/claude-sonnet-5` (or the actual model doing the write) everywhere
     — one consistent actor string across all four docs. Don't add `verified` or `stale_after`;
     these docs go stale on the next commit, and inventing a TTL is ceremony, not signal.
   - Anything you'd otherwise be tempted to stash as a narrative aside (a hazard, a gotcha, a
     "hard-won lesson") belongs in its own concept file, not folded into an existing doc's prose
     or into `manifest.json`. See step 6a.

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

6. **Write/update `kb/<slug>/manifest.json`**. This file is pipeline bookkeeping for step 2's
   short-circuit, not a knowledge concept — it stays plain JSON, outside OKF's `.md`
   conformance surface, and stays terse:
   ```json
   {
     "target_path": "<absolute target repo path>",
     "git_remote": "<remote url or null>",
     "last_crawl_commit": "<HEAD sha>",
     "last_crawl_date": "<ISO date>"
   }
   ```
   Do not add a narrative `note` field here. A hazard, gotcha, or other hard-won fact that
   doesn't fit one of the four docs is knowledge, and belongs in its own concept file (step 6a),
   not buried in this bookkeeping file where nothing will discover it later.

6a. **Write one concept file per durable hard-won fact** that doesn't belong inside one of the
    four docs' structure — a hazard that cost real work, a non-obvious gotcha, a fact future runs
    would otherwise relearn the hard way. Put these under `kb/<slug>/notes/<slug>.md`, one per
    fact, each with OKF frontmatter:
    ```yaml
    ---
    type: Hazard          # or: Reference, Note — pick what fits; types aren't centrally registered
    title: <short name>
    description: <one sentence>
    generated: { by: kb-generate/claude-sonnet-5, at: <ISO 8601 datetime> }
    tags: [<repo-area>, ...]
    ---
    ```
    followed by the actual explanation in the body. Skip this step entirely if a rerun turns up
    nothing new — most runs won't need it.

7. **Create `kb/<slug>/stories/` if it doesn't exist yet** (empty is fine — `slice-prd` populates
   it later).

8. **Write/update the bundle-root `kb/<slug>/index.md`** — the OKF directory listing (no
   frontmatter, except this root file MAY carry `okf_version: "0.2"`). List the four docs and
   `notes/` and `stories/` under headed sections, each entry using that concept's `description`:
   ```markdown
   ---
   okf_version: "0.2"
   ---

   # table-stakes knowledgebase

   * [Architecture](architecture.md) - <architecture.md's description>
   * [Module Map](module-map.md) - <module-map.md's description>
   * [Conventions](conventions.md) - <conventions.md's description>
   * [Key Files](key-files.md) - <key-files.md's description>
   * [Stories](stories/index.md) - sliced user stories and their status
   * [Notes](notes/) - hazards and hard-won facts, if any exist
   ```
   Regenerate this in full each run; don't hand-edit around a stale entry.

9. Report back to the user: what was generated, whether OpenSpec setup succeeded, and where the
   knowledgebase actually lives (`<target-repo-path>/docs/kb/`, symlinked from `kb/<slug>/` here).
