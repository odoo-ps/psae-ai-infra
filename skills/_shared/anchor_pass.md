# The Anchor Pass — shared procedure

The quality gate every Document Skill runs before it declares a draft finished.
Each Anchor is a read-only sub-agent that re-reads one source of truth and the
draft artifact, then reports drift. This file owns the *mechanics*; each skill
names its own anchor set, its own target artifact, and its own gate.

Drift is what context loss looks like in a long interview: a checklist item
discussed in conversation but never landed in the artifact; a principle
deferred-to-later that silently vanished; a role's required content
under-written because the conversation moved past it too fast. The interview is
linear by design (principle #10 keeps one question at a time) — but linear *and*
long is exactly where state erodes. The Anchor Pass is the recovery mechanism.

## Invocation

**ALL Agent calls go in ONE message, foreground only.** This is what makes the
pass an actual gate:

- **One message, N tool calls.** Emit every `Agent` call in a single assistant
  message. The harness runs tool calls inside one message concurrently and
  blocks the next turn until every one completes — that block is the gate. If
  you find yourself splitting anchors across turns (10 now, 4 later), the gate
  is broken: abort and re-issue all of them in one message.
- **Foreground only.** Never set `run_in_background: true` — it returns a task
  ID without waiting, defeating the gate.
- **Nothing that closes the gate in the same message.** The finish-line action
  must land in a later message, after reconciliation — same-message inclusion
  races the gate.

Each anchor:

- gets the absolute path of the target artifact as its sole prompt argument
- has read-only tools (Read, Grep, Glob, Bash) — MUST NOT edit anything
- returns a structured JSON report with `findings[]` (severity, location, issue,
  suggestion, tags) **as the anchor's final assistant message** — the return
  value IS the audit. Anchors must NOT write findings to a file (no Write, no
  `> file` redirection through Bash). When phrasing the prompt, do not ask an
  anchor to "save" or "write" the audit; ask it to *return* the JSON. Past runs
  have had anchors emit `echo '{...}' > audit.json` because the prompt or the
  `## Output` heading was misread as "produce an output file"; the wording in
  the anchor files and here exists to prevent that.

## Where anchors come from

Anchors are authored at `skills/_shared/anchors/<name>.md` in the Infra Repo.
Bootstrap copies each one into `.claude/agents/` at SessionStart, prefixed
`anchor-`, because Claude Code discovers sub-agents there and nowhere else — an
anchor left under `skills/` cannot be invoked and the gate silently never fires.

**Invoke an anchor by its frontmatter `name` (`qa-anchor`), never by filename.**
The `anchor-` prefix exists only so Bootstrap can remove exactly what it
installed without touching a consultant's own agent definitions in the same
directory. Renaming files does not change the handle; editing `name:` does.

## Reconciliation

0. **Verify completeness — the gate's self-check.** Before touching findings,
   confirm a JSON response from every anchor in the set (the `auditor` field in
   each payload should cover it). If any returned an error, no payload, or
   off-spec output, **re-call that single anchor in a new message** before
   moving on. Never reconcile from partial coverage — if any anchor didn't
   audit the artifact, the gate is open. Two consecutive failures of the same
   anchor surface as a `blocker` ("anchor X failed; cannot close the gate")
   rather than being silently dropped.
1. **Collect** all `findings` arrays.
2. **Dedupe by `tags`** — when two anchors flag the same underlying issue from
   different lenses, present it once and list every anchor that raised it. The
   tag namespace is: `principle:<n>`, `structure:<aspect>`, `role:<slug>`,
   `checklist:<artifact>`, `ts:<id>`, `drift:<pattern>`.
3. **Bucket by severity** — `blocker` gates the finish line; `nit` is non-gating.
4. **Surface blockers one at a time** to the user, per principle #10, with a
   single-question patch-or-override ask.
5. **Apply approved patches** to the artifact (only the main Claude edits, never
   the anchors).
6. **Re-run affected anchors** when a patch touches their domain, to confirm the
   patch resolved the finding without introducing a new one.
7. **Land nits** in a final summary appended to the artifact or its builder:
   ```
   ## Anchor Pass — Open Nits (<date>)
   - [<anchor-name>] <issue> — <suggestion>
   ```
8. **Close the gate** once no blockers remain.

## When to skip

- User explicitly asks: `--skip-audit`, "fast-mode", or equivalent. Record the
  skip where the skill specifies (each skill names its own marker).
- The artifact is a fix-iteration to an already-anchored artifact and the only
  change responds to a lint failure — the Anchor Pass is for *decisions*, not
  fix-loop mechanics.

## Limit

Anchors catch **artifact-vs-source-of-truth drift**, not **conversation-vs-
artifact drift**. If a decision was deliberated then never landed, the anchors
catch that as "checklist item with no entry". What they cannot catch is a
decision recorded in the artifact but contradicted by a later conversation turn
that also never reached the artifact. This is accepted: the pass re-anchors
against the artifact-as-frozen-document, which is what the finish line actually
gates on.
