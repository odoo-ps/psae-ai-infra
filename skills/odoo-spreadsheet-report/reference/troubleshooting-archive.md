# Spreadsheet Report — Troubleshooting Archive

Fixed, obsolete, or version-retired troubleshooting entries. Not loaded by the skill at run time — consult only when investigating "did we hit this before?"

**ID space is shared with the active file** ([`troubleshooting.md`](troubleshooting.md)) — never reused. Entries here keep the ID they had when active.

**Promotion criteria for new archival:**
- Status `fixed` for 90+ days with no recurrence (`Last confirmed` is the recurrence trigger — bumping it on re-encounter takes the entry back to active).
- Whole version-specific section retired when no supported deployment runs that Odoo version.
- Cause has been promoted to a principle, a role checklist, or a sibling reference file (insight is now codified upstream — common destinations for this skill: [`design_system.md`](design_system.md) for layout patterns, [`cf_operators.md`](cf_operators.md) for operator-name confusion).

When archiving, set `Status: fixed YYYY-MM-DD` (or `obsolete YYYY-MM-DD`) and add a one-line `Retired: <reason>` at the end of the entry.

---

*(No archived entries yet — the active file was reformatted from a 121-line mixed-content log to the 4-line shape on 2026-06-13; content that did not fit the troubleshooting shape was promoted to `design_system.md`, `cf_operators.md`, and the skill's SKILL.md rather than archived.)*
