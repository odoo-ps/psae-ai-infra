#!/usr/bin/env python3
"""
PreToolUse guard for Edit | Write | MultiEdit  (functional-consultant guardrail).

A deterministic backstop behind the settings.json permission rules:

  * Hard-deny the technical consultant's territory (controllers, security,
    JS/OWL, the manifest, and the read-only Odoo source) regardless of intent.
  * For other Python (models, wizards, tests, ...), allow ONLY a small additive
    edit: a field, a constraint, a short compute. Block anything that adds a new
    model, overrides an ORM method, defines a controller route, or adds more
    than a small change's worth of lines.
  * For XML, allow text / label / wording tweaks and small inherited-view
    records; block new actions, menus, reports, QWeb templates, and any record
    that is not an ir.ui.view (structural surgery / seed data / security).

This is a backstop, not the primary gate: the agent self-judges the requirement
first (see the functional-edits skill) and the human confirms every `ask`. The
floor only catches edits that are unmistakably the technical consultant's job.
"""
import json
import re
import sys

# A small functional change is a field, a constraint, or a short compute.
# Counted as GROSS added non-blank, non-comment lines (so a padded old_string
# can't offset a large addition). Tests get a larger ceiling for fixtures.
MAX_ADDED_LINES = 20
MAX_TEST_ADDED_LINES = 80

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


def nonblank_lines(text):
    return [s for s in (ln.strip() for ln in text.splitlines())
            if s and not s.startswith("#")]


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        # Unparseable input: stay silent, defer to the settings.json rules.
        sys.exit(0)

    ti = data.get("tool_input", {}) or {}
    path = ti.get("file_path", "") or ""

    added = []
    if isinstance(ti.get("content"), str):       # Write
        added.append(ti["content"])
    if isinstance(ti.get("new_string"), str):    # Edit
        added.append(ti["new_string"])
    for e in (ti.get("edits") or []):            # MultiEdit
        if isinstance(e, dict) and isinstance(e.get("new_string"), str):
            added.append(e["new_string"])
    added_text = "\n".join(added)

    # 1) Technical consultant's territory -> hard deny (defence in depth with
    #    the settings.json deny rules). Read-only-src segment is matched anywhere
    #    so a relative path can't slip past an absolute anchor.
    hard = [
        (r"(^|/)controllers/", "controllers / routes"),
        (r"(^|/)security/", "security: access rights, record rules, groups"),
        (r"(^|/)static/src/", "JavaScript / OWL front-end code"),
        (r"__manifest__\.py$", "the manifest: dependencies, version, install"),
        (r"(^|/)src/(odoo|enterprise|themes)/", "read-only Odoo source"),
    ]
    for pat, why in hard:
        if re.search(pat, path):
            deny(REFERRAL.format(path=path, why=why))

    # 2) Python (models, wizards, tests, ...): small additive edits only.
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
        for pat, why in major:
            if re.search(pat, added_text, re.M):
                deny(REFERRAL.format(path=path, why=why))

        is_test = bool(re.search(r"(^|/)tests/", path))
        cap = MAX_TEST_ADDED_LINES if is_test else MAX_ADDED_LINES
        n = len(nonblank_lines(added_text))
        if n > cap:
            deny(REFERRAL.format(
                path=path,
                why="it adds ~%d lines - more than a field / constraint / "
                    "short compute%s" % (n, " / focused test" if is_test else "")))
        sys.exit(0)  # small Python change -> settings.json 'ask' confirms

    # 3) XML: block structural surgery; allow wording tweaks and small
    #    inherited-view records (the functional bread-and-butter).
    if path.endswith(".xml"):
        structural = [
            (r"<menuitem\b", "it adds a menu"),
            (r"<act_window\b", "it adds a window action"),
            (r"<report\b", "it adds a report action"),
            (r"<template\b", "it adds a QWeb template (view / report / website page)"),
            (r"<delete\b", "it deletes records"),
        ]
        for pat, why in structural:
            if re.search(pat, added_text):
                deny(REFERRAL.format(path=path, why=why))

        # A <record> is allowed only when every record it adds is an ir.ui.view
        # (an inherited view: filters, group-bys, field order, layout). Actions,
        # menus, security, crons, mail templates, sequences -> refer.
        if re.search(r"<record\b", added_text):
            models = re.findall(
                r"<record\b[^>]*?\bmodel=[\"']([^\"']+)[\"']", added_text)
            n_records = len(re.findall(r"<record\b", added_text))
            if len(models) != n_records or any(m != "ir.ui.view" for m in models):
                deny(REFERRAL.format(
                    path=path,
                    why="it adds a non-view record (action / menu / security / "
                        "seed data)"))
        sys.exit(0)  # view tweak or in-place wording -> settings.json 'ask'

    # 4) i18n and anything else -> allow.
    sys.exit(0)


if __name__ == "__main__":
    main()
