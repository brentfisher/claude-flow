---
name: slice-prd
description: Slice a PRD document into discrete, independently-implementable user stories for a target codebase, using its flow knowledgebase and prior OpenSpec decisions as context. Use when the user says "slice this PRD", "break this PRD into stories", or "run slice-prd", giving a PRD file and a target repo.
---

# slice-prd

`/slice-prd <target-repo-path> <prd-path>`

## Steps

1. **Resolve the repo slug** the same way `kb-generate` does (git remote basename, or sanitized
   path basename). If `kb/<slug>/manifest.json` doesn't exist, stop and tell the user to run
   `/kb-generate <target-repo-path>` first — don't try to slice blind.

2. **Gather context** — read, don't guess:
   - `kb/<slug>/architecture.md`, `module-map.md`, `conventions.md`, `key-files.md`.
   - `<target-repo-path>/openspec/changes/archive/**`, `<target-repo-path>/openspec/changes/**`
     and `<target-repo-path>/openspec/specs/**` if they exist (`Grep`/`Read`, not vector search —
     this KB is small enough that plain text search finds what's relevant). Archived changes are
     decisions already made and shipped, in-flight `changes/` are decisions made but not yet
     landed, and `specs/` is the current state; use all three so you don't propose a story that
     redoes something already decided or already rejected. In-flight changes carry a second risk
     the archive doesn't: those decisions aren't in the code yet, so a story sliced against
     today's files may be standing on ground that is about to move. Check for that explicitly —
     where it's true, name the colliding change in the story's Notes and say which lands first.
   - Note the path: OpenSpec archives to `openspec/changes/archive/`, **not** `openspec/archive/`.
     If `openspec/` exists but these globs match nothing, say so in the final report (step 7
     makes this a required line) rather than silently slicing as if there were no prior
     decisions — an empty result and a wrong path look identical from here.
   - `<target-repo-path>/openspec/config.yaml` if present — its `context:` block carries
     project-wide conventions the repo owner wants applied to generated artifacts.
   - The PRD itself at `<prd-path>`.

3. **Slice the PRD into stories.** Each story should be:
   - Independently implementable by one agent working on its own branch (no story should require
     another story to land first, unless genuinely unavoidable — call that out explicitly if so).
   - Scoped to a coherent, reviewable PR — not "the whole PRD" and not "rename one variable".
   - Given concrete, testable acceptance criteria (checkable from a diff or by running the app).

4. **Determine the next story id.** List `kb/<slug>/stories/STORY-*.md`, find the highest `NNN`,
   continue from there (zero-padded to 3 digits, e.g. `STORY-004`). Start at `STORY-001` if none
   exist.

5. **Write one file per story** at `kb/<slug>/stories/STORY-NNN-<slug>.md`, using
   `templates/story.md.tmpl` as the structure — the plugin root's `templates/`, a sibling of
   `skills/` and the same directory `kb-generate` draws its four templates from, **not** a
   directory inside this skill. Fill in `id`, `title`, `status: pending`,
   `prd_source: <prd-path>`, `created`/`updated` (today, ISO date), a real summary, and real
   acceptance criteria. Leave `branch`, `worktree_path`, `base_branch`, `pr_url`,
   `is_architectural` and `approach_summary` present and `null` — `kickoff` and `open-prs` fill
   those in and read those keys, so don't drop them. In the **Notes** section, cite specific
   knowledgebase or OpenSpec sources that constrain this story, e.g. "conventions.md: uses
   repository pattern, see UserRepository" or "openspec/changes/archive/2026-06-caching:
   rejected in-memory cache, use redis".
   - **When a story touches ground a prior decision already covers, classify the relationship in
     one sentence** — this story *preserves* / *extends* / *revises* / *supersedes* decision X —
     naming the decision by file and heading, e.g. "`openspec/changes/<slug>/design.md`
     **Decision 4** is the decision this story preserves; change only which named constant
     expresses the behaviour, not its semantics." A story that reimplements a decided behaviour
     reads from the diff alone like it's overturning it, and a story that silently contradicts an
     archived or in-flight decision is the most expensive failure mode of slicing — it surfaces
     in review, if at all.

6. **Regenerate `kb/<slug>/stories/INDEX.md`** — a simple generated table (id, title, status) over
   all story files in that directory. This file is never hand-edited; always fully regenerate it.

7. Report back to the user: how many stories were created, their ids/titles, and remind them the
   next step is `/kickoff <target-repo-path>`. Two things the report must state as well, every
   run:
   - **Which OpenSpec sources you actually read** — one line each for
     `openspec/changes/archive/`, non-archived `openspec/changes/` and `openspec/specs/`, each
     marked *present* (with what you found in it), *empty*, or *absent*. "There were no prior
     decisions" and "I looked in the wrong place" produce identical silence otherwise, and the
     second is a correctness failure the user has no way to see.
   - **Where the stories live, and that they're local-only**: `kb/<slug>/stories/` inside this
     plugin, outside the target repo and not under version control. If the user asks to commit
     the stories, say plainly that there's nothing to commit them to — the PRD is in their repo,
     the stories aren't — and that they exist on this machine only.
