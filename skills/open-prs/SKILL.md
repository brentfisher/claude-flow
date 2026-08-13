---
name: open-prs
description: Push completed story branches and open pull requests for them, never auto-merging. Use when the user says "open PRs", "run open-prs", or after a kickoff-spawned agent finishes a story — also invoked automatically by kickoff when a story agent completes.
---

# open-prs

Two invocation shapes:

- `/open-prs <target-repo-path> <story-id>` — process exactly one story (this is how `kickoff`
  auto-chains after a background agent finishes).
- `/open-prs <target-repo-path>` — catch-up mode: scan all stories for this repo with
  `status: ready-for-pr` and no `pr_url` set, and process each. Use this if a session was closed
  before an agent finished, or to double-check nothing was missed.

## Steps (per story)

1. **Resolve the repo slug** as in `kb-generate`.

2. **Read the story file** at `kb/<slug>/stories/STORY-NNN-*.md`. Confirm `status: ready-for-pr`
   and `branch`/`base_branch` are set (`kickoff` writes these before spawning the story agent). If
   either is missing, something didn't finish its bookkeeping — report this to the user rather
   than guessing.

3. **Compose the PR title and body.** Title = the story's `title` field. Body: a short summary
   from the story's own summary section, the acceptance criteria as a checklist, a link back to
   `prd_source`, and — if `is_architectural: true` — a line calling out that an OpenSpec change
   proposal was added at `openspec/changes/<feature-slug>/` in this branch, so reviewers know to
   look at it alongside the code. Write the body to a scratch temp file for this one call.

4. **Open the PR:**
   ```
   bash scripts/prs/open_pr.sh <target-repo-path> <branch> <base_branch> "<title>" <body-file>
   ```
   This pushes the branch and runs `gh pr create`. If `gh` isn't installed or not authenticated,
   the script fails with a clear error — surface that to the user directly (install: `brew install
   gh`, then `gh auth login`) rather than retrying blindly.

5. **Update the story file**: `status: pr-opened`, `pr_url` set to the URL `gh pr create` printed,
   `updated` to today.

6. **Clean up the worktree.** If `worktree_path` is set and still exists,
   `git -C <target-repo-path> worktree remove <worktree_path>`. The branch itself is untouched —
   its commits are already pushed and live on the remote/PR. If removal fails (e.g. uncommitted
   changes snuck in), warn the user rather than forcing it.

7. **Regenerate `kb/<slug>/stories/INDEX.md`.**

8. **Never merge the PR.** This skill's job ends at opening it for review.

9. Report back: which PR(s) were opened, with URLs, and any stories that were skipped along with
   why (missing branch, `gh` unavailable, etc.).
