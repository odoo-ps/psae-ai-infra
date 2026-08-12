#!/usr/bin/env python3
"""
PreToolUse guard for Bash  (functional-consultant guardrail).

Blocks deployment / database / dependency commands that are the technical
consultant's job, the user's job in the Odoo.sh UI, or that simply don't work
on Odoo.sh:

  * git push / merge / rebase, and checkout|switch to staging|production
    (promotion is the user's job in the Odoo.sh UI; `git push` fails on
    Odoo.sh - use `odoosh-push` to persist work on the dev branch).
  * pip / npm / yarn / pnpm installs (dependency changes are technical).
  * odoo-bin scaffold (creating a module), odoo-bin with -d / --database
    (incl. the attached -dDBNAME form), and createdb / dropdb / CREATE|DROP|
    ALTER DATABASE / DROP|TRUNCATE TABLE issued through psql (the database is
    injected - never re-wire or destroy it).

The day-to-day commands - `odoo-bin -u` / `--test-tags`, `psql` reads, and
`odoosh-push` (to the dev branch) - are handled by settings.json (allow / ask)
and are intentionally NOT blocked here. Patterns are word-anchored so an
innocent mention (e.g. the word "scaffold" inside a commit message) is fine.

The permissionDecision is conveyed via the printed stdout JSON; the script
always exits 0. Do not "fix" it into a non-zero exit - that would fail open.
"""
import json
import re
import sys


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        sys.exit(0)

    # Anything unexpected in the payload must leave `cmd` empty rather than
    # raise. A hook that raises exits non-zero, and Claude Code ignores a hook
    # that errors — so a crash is a silently OPEN guardrail.
    tool_input = data.get("tool_input") if isinstance(data, dict) else None
    cmd = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    cmd = cmd if isinstance(cmd, str) else ""

    # Global options may sit between `git` and its subcommand, so `git push`
    # and `git -C /some/repo push` are the same command. Matching only the
    # adjacent form left the `-C` spelling reaching the network — the Corpus
    # itself used it once, to probe push access.
    git = r"\bgit\s+(?:(?:-[cC]|--exec-path|--git-dir|--work-tree)[=\s]\S+\s+|--no-pager\s+|--bare\s+)*"

    block = [
        git + r"push\b",
        git + r"merge\b",
        git + r"rebase\b",
        git + r"(checkout|switch)\b[^\n]*\b(production|staging)\b",
        r"\bpip[0-9.]*\s+install\b",
        r"\bnpm\s+(install|i|ci|add)\b",
        r"\b(yarn|pnpm)\s+(add|install|i)\b",
        r"\bodoo-bin\s+scaffold\b",
        r"\bodoo-bin\b[^\n]*\s-d(?=$|[\s=]|\w)",        # -d mydb / -d=mydb / -dmydb
        r"\bodoo-bin\b[^\n]*\s--database(=|\s|$)",
        r"\b(createdb|dropdb)\b",
    ]
    blocked = any(re.search(b, cmd) for b in block)

    # Destructive DB SQL, but only when actually run through psql, so prose
    # (e.g. the words "drop table" in a commit message) is not false-blocked.
    if not blocked and re.search(r"\bpsql\b", cmd) and re.search(
            r"(?i)\b((create|drop|alter)\s+database|(drop|truncate)\s+table)\b", cmd):
        blocked = True

    if blocked:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Blocked by the functional guardrail: this is a deployment / "
                    "database / dependency command (push, merge, branch promotion, "
                    "module scaffold, DB wiring or destruction, or a package "
                    "install). It is the technical consultant's job, or yours in "
                    "the Odoo.sh UI. To persist work on the dev branch use "
                    "`odoosh-push`; to apply changes use "
                    "`odoo-bin -u <module> --stop-after-init --no-http`."
                ),
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
