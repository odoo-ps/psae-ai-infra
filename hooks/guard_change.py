#!/usr/bin/env python3
"""
PreToolUse guard for Edit | Write | MultiEdit  (functional-consultant guardrail).

A deterministic backstop behind the settings.json permission rules:

  * Hard-deny the technical consultant's territory (controllers, security,
    JS/OWL, the manifest, and the read-only Odoo source) regardless of intent.
    Paths are resolved before matching, so a relative path cannot slip past an
    absolute anchor.
  * For other Python (models, wizards, tests, ...), allow ONLY a small additive
    edit: a field, a constraint, a short compute. Block anything that adds a new
    model, overrides an ORM method, defines a controller route, removes an
    existing method, or adds more than a small change's worth of lines.
  * For XML, allow wording tweaks and *cosmetic* inherited-view edits; block new
    actions, menus, reports, QWeb templates, standalone views, structural
    replacement, and any record that is not an ir.ui.view.

Edits are classified DIFFERENTIALLY: the guard diffs the text being replaced
against its replacement and reasons about the lines that genuinely changed. This
matters in both directions. It stops the guard denying a one-word label change
buried in a thirty-line method (which taught consultants the guard was noise),
and it lets the guard see deletions at all — a hook that only inspects the new
text can be bypassed by replacing a method body with nothing.

Differential counting is also STRICTER than counting the replacement text
wholesale. The harness requires `old_string` to match the file byte-for-byte, so
it cannot be padded with fabricated context to offset a large addition: every
line it contains is genuinely already in the file. See ADR 0002.

This is a backstop, not the primary gate: the agent self-judges the requirement
first (see the functional-edits skill) and the human confirms every `ask`. The
floor only catches edits that are unmistakably the technical consultant's job.
"""
import difflib
import json
import os
import re
import sys

# A small functional change is a field, a constraint, or a short compute.
# Counted as lines that genuinely CHANGED (added or rewritten), never as the
# gross size of the replacement text. Tests get a larger ceiling for fixtures.
MAX_ADDED_LINES = 20
MAX_TEST_ADDED_LINES = 80

# The positions that only ever ADD to a view or retune an existing element.
# `replace` is excluded deliberately: it is the one position that destroys what
# the technical consultant wrote, and `attributes` covers the legitimate cases.
COSMETIC_POSITIONS = {"after", "before", "inside", "attributes", "move"}

# The Document Skills' output folders at the Project Repo root. What lands
# there is a deliverable, not deployable code: none of it carries a manifest,
# so the server never loads it. A specification's builder script IS the
# deliverable, and measuring it against the Python floor denies the skill its
# own output — so the floor stops at these folders. Creating a module inside
# one is still impossible: `__manifest__.py` is hard-denied everywhere.
DOCUMENT_DIRS = {"specifications", "mocks", "handovers",
                 "spreadsheet_reports", "plans"}

REFERRAL = (
    "MAJOR CHANGE - blocked by the functional guardrail.\n"
    "The edit to '{path}' goes beyond a small functional change ({why}). "
    "Maintaining the architecture the technical consultant built is part of "
    "your job, so this one is theirs.\n"
    "Stop here and refer it to the technical consultant. I can draft a short "
    "handover: the client's intent plus the models / fields it would touch."
)


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def project_dir():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def resolve(path):
    """Absolute, normalised form of a tool-supplied path.

    Tool inputs carry whatever the agent typed. `../odoo/addons/sale/x.py` from
    /home/odoo/src/user is the read-only Odoo source, but matches no pattern
    anchored on `src/odoo/` until it is resolved.
    """
    if not isinstance(path, str) or not path:
        return ""
    if not os.path.isabs(path):
        path = os.path.join(project_dir(), path)
    return os.path.normpath(path)


def significant(lines):
    """Non-blank, non-comment lines — the ones that carry meaning."""
    return [s for s in (ln.strip() for ln in lines)
            if s and not s.startswith("#")]


def diff_lines(old, new):
    """(added, removed) — the lines that genuinely changed.

    A rewritten line counts as both removed and added, which is correct: the
    consultant is responsible for what it now says.
    """
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    added, removed = [], []
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ("insert", "replace"):
            added.extend(new_lines[j1:j2])
        if tag in ("delete", "replace"):
            removed.extend(old_lines[i1:i2])
    return added, removed


def edit_pairs(tool_input, path):
    """Every (before, after) pair this tool call would apply."""
    pairs = []

    if isinstance(tool_input.get("content"), str):        # Write
        before = ""
        try:                                             # overwrite: diff on disk
            with open(path, encoding="utf-8") as fh:
                before = fh.read()
        except OSError:
            pass                                         # new file: all additive
        pairs.append((before, tool_input["content"]))

    if isinstance(tool_input.get("new_string"), str):     # Edit
        pairs.append((tool_input.get("old_string") or "", tool_input["new_string"]))

    for edit in (tool_input.get("edits") or []):          # MultiEdit
        if isinstance(edit, dict) and isinstance(edit.get("new_string"), str):
            pairs.append((edit.get("old_string") or "", edit["new_string"]))

    return pairs


# --- XML helpers -------------------------------------------------------------

# The `/>` branch must bind to a self-closing RECORD, not to the first
# self-closing <field/> inside one — `[^>]*` cannot cross the opening tag's `>`.
# Getting this wrong truncates the block after the first self-closing field, so
# type / mode / active fall outside it and every check on them silently passes.
RECORD_BLOCK = re.compile(r"<record\b[^>]*/>|<record\b[^>]*>.*?</record>", re.S)


def field_value(block, name):
    """Value of <field name="..."> — its eval= attribute or its element text.

    Resolve the opening tag FIRST, then read from it. Matching straight through
    to a `</field>` lets a self-closing `<field name="active" eval="False"/>`
    swallow the *next* field's body and report that as its value.
    """
    tag = re.search(r"<field\b[^>]*\bname=[\"']%s[\"'][^>]*>" % name, block)
    if not tag:
        return None
    opening = tag.group(0)

    evaluated = re.search(r"\beval=[\"']([^\"']*)[\"']", opening)
    if evaluated:
        return evaluated.group(1).strip()
    if opening.rstrip().endswith("/>"):
        return None                       # self-closing, carries no value

    closing = re.search(r"</field>", block[tag.end():], re.S)
    if not closing:
        return None
    return block[tag.end():tag.end() + closing.start()].strip()


def check_view_record(block, path):
    """A record is cosmetic only when it EXTENDS an existing backend view."""
    model = re.search(r"<record\b[^>]*?\bmodel=[\"']([^\"']+)[\"']", block)
    if not model or model.group(1) != "ir.ui.view":
        deny(REFERRAL.format(
            path=path,
            why="it adds a non-view record (action / menu / security / seed data)"))

    if not re.search(r"<field\b[^>]*\bname=[\"']inherit_id[\"']", block):
        deny(REFERRAL.format(
            path=path,
            why="it declares a standalone view rather than extending an "
                "existing one (no inherit_id)"))

    mode = field_value(block, "mode")
    if mode and mode.strip("'\"") == "primary":
        deny(REFERRAL.format(
            path=path,
            why="it declares a primary view — inheriting the arch but detaching "
                "from the original"))

    vtype = field_value(block, "type")
    if vtype and vtype.strip("'\"") == "qweb":
        deny(REFERRAL.format(
            path=path,
            why="it declares a QWeb template (report layout / website page) as "
                "an ir.ui.view record"))

    active = field_value(block, "active")
    if active is not None and active.strip("'\"").lower() in ("false", "0"):
        deny(REFERRAL.format(
            path=path,
            why="it deactivates an existing view"))


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        # Unparseable input: stay silent, defer to the settings.json rules.
        sys.exit(0)

    # Anything unexpected in the payload must land here as an empty dict rather
    # than an AttributeError. A hook that raises exits non-zero, and Claude Code
    # ignores a hook that errors — so a crash is a silently OPEN guardrail.
    if not isinstance(data, dict):
        sys.exit(0)
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        sys.exit(0)

    raw_path = tool_input.get("file_path", "") or ""
    path = resolve(raw_path)

    pairs = edit_pairs(tool_input, path)
    added, removed = [], []
    for before, after in pairs:
        a, r = diff_lines(before, after)
        added.extend(a)
        removed.extend(r)
    added_text = "\n".join(added)
    removed_text = "\n".join(removed)

    # 1) Technical consultant's territory -> hard deny (defence in depth with
    #    the settings.json deny rules). Matched on the RESOLVED path.
    hard = [
        (r"(^|/)controllers/", "controllers / routes"),
        (r"(^|/)security/", "security: access rights, record rules, groups"),
        (r"(^|/)static/src/", "JavaScript / OWL front-end code"),
        (r"__manifest__\.py$", "the manifest: dependencies, version, install"),
        (r"(^|/)src/(odoo|enterprise|themes)/", "read-only Odoo source"),
    ]
    for pattern, why in hard:
        if re.search(pattern, path):
            deny(REFERRAL.format(path=raw_path, why=why))

    #    Only the Project Repo is writable on Odoo.sh. This catches every escape
    #    from it, including ones the patterns above don't name.
    root = os.path.normpath(project_dir())
    if path and not (path == root or path.startswith(root + os.sep)):
        deny(REFERRAL.format(
            path=raw_path,
            why="it writes outside %s — the only writable tree on Odoo.sh" % root))

    # 2) A Document Skill's own output folder -> allow. Judged by where it
    #    lands, because a builder script is indistinguishable from any other
    #    Python by content and is meant to be large.
    #
    #    Guarded on a non-empty path: relpath("") raises, and a payload with no
    #    file_path must leave here in silence rather than crash. A hook that
    #    raises exits non-zero, and Claude Code ignores a hook that errors.
    if path and os.path.relpath(path, root).split(os.sep)[0] in DOCUMENT_DIRS:
        sys.exit(0)

    # 3) Python (models, wizards, tests, ...): small additive edits only.
    if path.endswith(".py"):
        major = [
            (r"(^|[:\s])_name\s*=\s*['\"]", "it defines a new model (_name)"),
            (r"\bdef\s+_?(create|write|unlink|copy|default_get|read_group|search"
             r"|name_create|name_search|web_save|fields_view_get|get_view)\b\s*\(",
             "it overrides an ORM method"),
            (r"\bsuper\([^)]*\)\.(create|write|unlink|copy|_create|_write|_unlink)\b",
             "it overrides an ORM method (super() call)"),
            (r"@(http\.)?route\b", "it defines a controller route"),
            (r"class\s+\w+\s*\([^)]*\bController\b", "it defines a controller"),
        ]
        for pattern, why in major:
            if re.search(pattern, added_text, re.M):
                deny(REFERRAL.format(path=raw_path, why=why))

        if re.search(r"^\s*(def|class)\s+\w+", removed_text, re.M):
            deny(REFERRAL.format(
                path=raw_path,
                why="it removes an existing method or class"))

        is_test = bool(re.search(r"(^|/)tests/", path))
        cap = MAX_TEST_ADDED_LINES if is_test else MAX_ADDED_LINES
        n = len(significant(added))
        if n > cap:
            deny(REFERRAL.format(
                path=raw_path,
                why="it changes ~%d lines - more than a field / constraint / "
                    "short compute%s" % (n, " / focused test" if is_test else "")))
        sys.exit(0)  # small Python change -> settings.json 'ask' confirms

    # 4) XML: block structural surgery; allow wording tweaks and cosmetic
    #    inherited-view edits (the functional bread-and-butter).
    if path.endswith(".xml"):
        structural = [
            (r"<menuitem\b", "it adds a menu"),
            (r"<act_window\b", "it adds a window action"),
            (r"<report\b", "it adds a report action"),
            (r"<template\b", "it adds a QWeb template (view / report / website page)"),
            (r"<delete\b", "it deletes records"),
        ]
        for pattern, why in structural:
            if re.search(pattern, added_text):
                deny(REFERRAL.format(path=raw_path, why=why))

        if re.search(r"<(record|menuitem|template|act_window|report)\b", removed_text):
            deny(REFERRAL.format(
                path=raw_path,
                why="it removes an existing record / menu / template"))

        # Every position must only add to the view or retune an element on it.
        for position in re.findall(r"\bposition=[\"']([^\"']+)[\"']", added_text):
            if position not in COSMETIC_POSITIONS:
                deny(REFERRAL.format(
                    path=raw_path,
                    why="it uses position=\"%s\", which reshapes the existing "
                        "view rather than extending it" % position))

        # A <record> is allowed only when it EXTENDS an existing backend view.
        if re.search(r"<record\b", added_text):
            whole = "\n".join(after for _, after in pairs)
            for block in RECORD_BLOCK.findall(whole):
                opening = block.split(">", 1)[0]
                if opening in added_text:
                    check_view_record(block, raw_path)
        sys.exit(0)  # view tweak or in-place wording -> settings.json 'ask'

    # 5) i18n and anything else -> allow.
    sys.exit(0)


if __name__ == "__main__":
    main()
