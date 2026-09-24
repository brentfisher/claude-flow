---
name: kickoff
description: Fan out approved user stories to parallel background agents, each working in an isolated git worktree on its own branch, after a short human-approval checkpoint. Use when the user says "kick off the stories", "run kickoff", or "start implementing the stories" for a target repo that already has sliced stories.
---

# kickoff

`/kickoff <target-repo-path> [story-ids...]`

**Worktrees are manual.** `Agent`'s `isolation: "worktree"` and `EnterWorktree` only anchor to
this session's own repo (and fail since `flow` isn't one) — so use `git worktree add` + plain
`Agent` calls with absolute paths (verified end to end).

**Token discipline:** read frontmatter before bodies, read KB docs once per run and only the
sections a story's Notes cite, and never paste into agent prompts what the agent can read itself.

## Steps

1. **Candidates.** Resolve the slug as in `kb-generate`. If `story-ids` were given, use exactly
   those; else `grep -l '^status: pending' kb/<slug>/stories/STORY-*.md`. Don't read non-candidate
   story bodies. None → tell the user and stop.

2. **Pin the base branch:** `git -C <target-repo-path> rev-parse --abbrev-ref HEAD`. Every story
   branches from and PRs into this. It's the *checked-out* branch, not the default — confirm with
   the user if it looks unintentional.

3. **Approach summary per candidate** (analysis only, no code):
   - If `approach_summary` and `is_architectural` are already non-null (left pending from an
     earlier run), reuse them.
   - Otherwise read the story, plus `module-map.md` once per run. For conventions/architecture,
     `grep -n '^## '` the doc and `Read` (offset/limit) only the sections the story's **Notes**
     cite. Open `architecture.md` only for likely-architectural stories.
   - Write 2-4 sentences: approach + files/modules touched.
   - `is_architectural: true` iff **any** of: new service/module, changed public API or data
     model, new external dependency, cross-cutting refactor touching multiple modules' contracts.
   - Edit both into frontmatter; leave `status: pending`.

4. **Approval gate — exactly one.** One `AskUserQuestion`, `multiSelect: true`, one option per
   story (label = id + short title, description = approach summary, prefixed `[architectural]`
   when true). No agent before it returns; no per-story gates after. Unselected stories stay
   `pending` (offered again next run) — don't mark rejected or delete.

5. **Launch approved stories.**
   - One `Bash` call creating all worktrees, each outside the target repo (e.g. a sibling dir):
     `git -C <target-repo-path> worktree add <worktree-path> -b <story-branch> <base-branch>`
   - One Edit per story file: `status: in-progress`, `branch`, `worktree_path`, `base_branch`
     (persisted so `open-prs` never re-derives it).
   - Spawn all agents in **one message**: plain `Agent`, **no `isolation` param**, background,
     `model: "sonnet"` when `is_architectural` is false (omit `model` for architectural stories —
     they inherit this session's model). Don't wait on them. Each prompt states (reference paths — don't paste story/KB content the
     agent can read itself):
     - No isolated cwd: every `Bash` is `cd <worktree-path> && ...`; every Read/Write/Edit uses
       absolute paths under `<worktree-path>`.
     - Its story file's absolute path (`/Users/brent/flow/kb/<slug>/stories/STORY-NNN-*.md`) —
       read it for acceptance criteria and approach summary.
     - Base branch and its branch name.
     - Conventions: absolute path to `kb/<slug>/conventions.md` plus the `## ` section headings
       relevant to this story — read only those (offset/limit), not the whole file.
     - If `is_architectural`: first `bash /Users/brent/flow/scripts/kb/openspec_setup.sh
       <worktree-path>` (**the worktree**, not the repo — `openspec/` usually isn't committed, so
       each worktree needs its own init). Then in the worktree
       `openspec new change <feature-slug> --description "<one line>"` and fill `proposal.md`,
       `design.md` (Mermaid diagram of the actual components changed), `tasks.md` per
       `openspec instructions <artifact> --change <feature-slug>`. Commit with the code.
     - Finish by: (a) committing all work in the worktree, (b) Editing the story file to
       `status: ready-for-pr`, `updated: <today>`. Don't push.
     - Final message is **one line only**: `STORY-NNN done: <branch> <short-sha> status=ready-for-pr`
       (or `STORY-NNN blocked: <reason>`). No summary report.

6. **Don't poll.** The harness notifies on each completion. On notification, immediately invoke
   `open-prs <target-repo-path> <story-id>` (non-destructive, never merges — no confirmation
   needed). If this session is gone by then, the story sits at `ready-for-pr` until
   `/open-prs <target-repo-path>` catch-up mode is run.

7. Tell the user which stories were kicked off and which were left pending.
