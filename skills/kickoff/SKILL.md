---
name: kickoff
description: Fan out approved user stories to parallel background agents, each working in an isolated git worktree on its own branch, after a short human-approval checkpoint. Use when the user says "kick off the stories", "run kickoff", or "start implementing the stories" for a target repo that already has sliced stories.
---

**Implementation note (found during build, overrides an earlier assumption):** the `Agent`
tool's `isolation: "worktree"` option — and `EnterWorktree` — anchor the worktree to the
*current session's own* git repo; they cannot target an arbitrary `<target-repo-path>` passed in
a prompt, and fail outright if the session itself isn't running inside a git repo (as `flow`
itself is not). Confirmed by testing. So step 5 below creates worktrees manually with
`git worktree add` and spawns plain `Agent` calls (no `isolation` param) with explicit
absolute-path instructions instead — verified working end to end.

# kickoff

`/kickoff <target-repo-path> [story-ids...]`

## Steps

1. **Resolve the repo slug** as in `kb-generate`. Load candidate stories from
   `kb/<slug>/stories/`: if `story-ids` were given, use exactly those; otherwise all stories with
   `status: pending`. If there are none, tell the user and stop.

2. **Pin the base branch once**, before anything else: run
   `git -C <target-repo-path> rev-parse --abbrev-ref HEAD` and record it. Every story agent
   branches from this same commit/branch, and every eventual PR targets it — don't let stories
   fan out from inconsistent starting points. Note this is the repo's **currently checked-out**
   branch, not necessarily its default branch — if the user runs `/kickoff` from a feature branch,
   that's what gets used, and it's internally consistent (every downstream step reads
   `base_branch` from the story file rather than re-deriving it), but worth confirming with the
   user if it looks unintentional.

3. **For each candidate story, produce a short approach summary** (don't write code yet — this is
   analysis only):
   - Read the story file plus the relevant knowledgebase docs (`kb/<slug>/architecture.md`,
     `module-map.md`, `conventions.md`).
   - Write 2-4 sentences: the intended approach and the files/modules likely touched.
   - Decide `is_architectural` using this checklist — true if the story involves **any** of:
     a new service/module, a changed public API or data model, a new external dependency, or a
     cross-cutting refactor touching multiple modules' contracts. Otherwise false. Don't leave
     this as a vague gut call — check the list.
   - Write both into the story file's frontmatter (`approach_summary`, `is_architectural`) via
     Edit, but leave `status: pending` for now — the approval gate in the next step decides what
     moves forward.

4. **Approval gate — mandatory, single checkpoint.** Call `AskUserQuestion` with
   `multiSelect: true`, one question listing every candidate story as an option (label = story id
   + short title, description = the approach summary, flagging `[architectural]` in the
   description when `is_architectural` is true). The user selects which stories to approve.
   - Do not spawn any agent before this gate returns.
   - Do not add further per-story gates after this one.
   - Stories not selected: leave `status: pending` — they'll be offered again next `/kickoff` run.
     Don't mark them rejected or delete them.

5. **For each approved story**, set `status: approved` then `status: in-progress` (Edit the story
   file). Then, from this session (using `Bash`, against `<target-repo-path>` which is a real repo
   even though this session's own directory isn't):
   ```
   git -C <target-repo-path> worktree add <worktree-path> -b <story-branch-name> <pinned-base-branch>
   ```
   Pick `<worktree-path>` outside the target repo's own tree (e.g. a sibling directory) and
   `<story-branch-name>` derived from the story id/title. Immediately Edit the story file to
   record `branch`, `worktree_path`, and `base_branch` (the value pinned in step 2 — persisting
   it here means `open-prs` never has to re-derive or guess it later). Then spawn one
   plain `Agent` tool call
   — **no `isolation` param** — run in background (don't set `run_in_background: false`; spawn all
   approved stories' agents, then stop, don't block waiting on them). The agent's prompt must
   state, explicitly and in full:
   - It has **no isolated cwd of its own** — every `Bash` call must `cd <worktree-path> && ...` or
     use absolute paths, and every `Read`/`Write`/`Edit` call must use absolute paths under
     `<worktree-path>`. Never rely on relative paths persisting between tool calls.
   - The absolute path to its own story file (e.g. `/Users/brent/flow/kb/<slug>/stories/STORY-NNN-*.md`)
     — this lives outside the worktree entirely, in `flow`'s own directory.
   - The pinned base branch name from step 2, and the branch name just created for it.
   - Its acceptance criteria and approach summary from the story file.
   - Relevant conventions from `kb/<slug>/conventions.md` (paste the relevant excerpt — the agent
     won't have `flow`'s files available either).
   - If `is_architectural` is true: before implementing, run
     `bash /Users/brent/flow/scripts/kb/openspec_setup.sh <worktree-path>` — **pointed at the
     worktree, not `<target-repo-path>`**. A worktree is a fresh checkout of the base branch; if
     `openspec/` was never committed to that branch (see `kb-generate`'s note on this — it isn't,
     by default), the worktree starts with no `openspec/` at all, so each architectural story's
     worktree needs its own init, verified working. Then, from inside `<worktree-path>`,
     `openspec new change <feature-slug> --description "<one line>"`, then fill in `proposal.md`,
     `design.md` (must include a Mermaid diagram of the actual change — new/modified components
     and their relationships, not a generic diagram), and `tasks.md` per
     `openspec instructions <artifact> --change <feature-slug>` guidance. Commit these alongside
     the code changes, on the same branch.
   - Its last two actions before finishing: (a) commit all work on its branch from inside
     `<worktree-path>`, (b) Edit its own story file (the absolute path given above) to set
     `status: ready-for-pr` and `updated` to today (`branch`/`worktree_path` are already recorded
     — no need to touch them). Do not push — the parent session handles pushing and PR creation.

6. **Don't poll.** The harness notifies this session when each background agent completes. You
   already know the branch name (you chose it before spawning) and the story's `branch` field
   confirms the agent finished its bookkeeping — no need to parse anything out of the agent's
   result text. When a completion notification for one of these story agents arrives — in this
   same session, possibly much later — immediately invoke the `open-prs` skill for that specific
   story
   (`<target-repo-path> <story-id>`) rather than waiting for the user to ask. This is the intended
   auto-chain from kickoff into PR-opening; opening a PR is non-destructive (never auto-merges),
   so there's no reason to add friction here. This auto-chain depends on this same session still
   being open when the notification arrives — if it isn't, the story simply sits at
   `status: ready-for-pr` until someone runs `/open-prs <target-repo-path>` in catch-up mode
   (no story-id), which is the reliable fallback and safe to run any time as a sanity check.

7. After spawning, tell the user which stories were approved and kicked off, and which were left
   pending.
