#!/usr/bin/env python3
"""Lint troubleshooting.md and troubleshooting-archive.md across skills.

Validates entry shape per principle #6:
  ### N. <symptom>
  Applies: <scope>. Status: <active|fixed YYYY-MM-DD|obsolete YYYY-MM-DD>. Last confirmed: <YYYY-MM-DD>.
  Cause: <sentence>.
  Fix: <sentence or snippet>.

Checks (per skill):
  - Each entry has all four required fields (heading, Applies/Status/Last-confirmed line, Cause, Fix).
  - IDs are unique across active + archive (combined namespace, never reused).
  - IDs are integers, sorted ascending within each file.
  - Soft caps on the active file: <= 250 lines, <= 35 active entries. Warns when exceeded.
  - Reports archive candidates: entries with Status: fixed YYYY-MM-DD older than 90 days.
  - Flags duplicate symptoms (heuristic — same normalised heading text).

ID namespaces are PER-SKILL. Plan-dev's #1 and spreadsheet-report's #1 are unrelated.

Exit codes:
  0   clean across all linted skills
  1   warnings only (soft caps, archive candidates) in at least one skill
  2   hard errors in at least one skill

Usage:
  ./_lint_troubleshooting.py                              # lint every skill with a troubleshooting file
  ./_lint_troubleshooting.py --skill odoo-plan-development # lint one skill
  ./_lint_troubleshooting.py --root <path>                 # override skills/ root
  ./_lint_troubleshooting.py --strict                      # warnings → errors
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

ACTIVE_LINE_CAP = 250
ACTIVE_ENTRY_CAP = 35
ARCHIVE_CANDIDATE_DAYS = 90

HEADING_RE = re.compile(r"^###\s+(\d+)\.\s+(.+?)\s*$")
SECTION_RE = re.compile(r"^##\s+(?!#)(.+?)\s*$")
APPLIES_RE = re.compile(
    r"^Applies:\s*(?P<scope>.+?)\.\s*"
    r"Status:\s*(?P<status>active|fixed\s+\d{4}-\d{2}-\d{2}|obsolete\s+\d{4}-\d{2}-\d{2})\.\s*"
    r"Last confirmed:\s*(?P<last>\d{4}-\d{2}-\d{2})\.\s*$"
)
CAUSE_RE = re.compile(r"^Cause:\s*(.+)$")
FIX_RE = re.compile(r"^Fix:\s*(.+)$")


@dataclass
class Entry:
    id: int
    heading: str
    line_no: int
    file: str
    section: str = ""
    applies: str = ""
    status: str = ""
    last_confirmed: str = ""
    cause: str = ""
    fix: str = ""
    errors: list[str] = field(default_factory=list)


def parse_file(path: Path) -> list[Entry]:
    """Walk a troubleshooting file and extract entries."""
    entries: list[Entry] = []
    if not path.exists():
        return entries

    lines = path.read_text(encoding="utf-8").splitlines()
    current: Entry | None = None
    current_section = ""
    state = "search"  # search → expect_applies → expect_cause → expect_fix → done

    for i, line in enumerate(lines, start=1):
        # Track the failure-surface section (## headings, not ###).
        # The file is intentionally organised by surface; IDs are ascending
        # within each section but not necessarily across sections.
        sm = SECTION_RE.match(line)
        if sm:
            current_section = sm.group(1)
            continue

        m = HEADING_RE.match(line)
        if m:
            # Finalise previous entry
            if current and state != "done":
                current.errors.append(
                    f"incomplete entry (state={state}); expected Applies/Cause/Fix block"
                )
                entries.append(current)
            current = Entry(
                id=int(m.group(1)),
                heading=m.group(2),
                line_no=i,
                file=path.name,
                section=current_section,
            )
            state = "expect_applies"
            continue

        if current is None:
            continue

        if state == "expect_applies":
            if not line.strip():
                continue  # tolerate blank lines between heading and Applies
            am = APPLIES_RE.match(line)
            if am:
                current.applies = am.group("scope")
                current.status = am.group("status")
                current.last_confirmed = am.group("last")
                state = "expect_cause"
            else:
                current.errors.append(
                    f"line {i}: expected 'Applies: …. Status: …. Last confirmed: YYYY-MM-DD.'"
                )
                state = "expect_cause"
            continue

        if state == "expect_cause":
            if not line.strip():
                continue
            cm = CAUSE_RE.match(line)
            if cm:
                current.cause = cm.group(1)
                state = "expect_fix"
            else:
                current.errors.append(f"line {i}: expected 'Cause: …' line")
                state = "expect_fix"
            continue

        if state == "expect_fix":
            if not line.strip():
                continue
            fm = FIX_RE.match(line)
            if fm:
                current.fix = fm.group(1)
                state = "done"
                entries.append(current)
                current = None
            else:
                current.errors.append(f"line {i}: expected 'Fix: …' line")
                state = "done"
                entries.append(current)
                current = None
            continue

    if current and state != "done":
        current.errors.append(f"incomplete entry (state={state}); expected Applies/Cause/Fix block")
        entries.append(current)

    return entries


def find_skills_root(start: Path) -> Path | None:
    """Walk up from start to find a directory with a `_shared/principles.md` sibling."""
    cur = start.resolve()
    while cur != cur.parent:
        if (cur / "_shared" / "principles.md").is_file():
            return cur
        cur = cur.parent
    return None


def discover_skills_with_troubleshooting(skills_root: Path) -> list[Path]:
    """Return every skill dir under skills_root that has reference/troubleshooting.md.

    Skips _shared/ (no skill there) and agents/ (anchor agents, not a skill).
    """
    skill_dirs: list[Path] = []
    for entry in sorted(skills_root.iterdir()):
        if not entry.is_dir() or entry.name in ("_shared", "agents"):
            continue
        if (entry / "reference" / "troubleshooting.md").exists():
            skill_dirs.append(entry)
    return skill_dirs


def lint_skill(skill_dir: Path) -> tuple[list[str], list[str], int, int]:
    """Lint one skill's troubleshooting pair. Returns (errors, warnings, active_count, line_count)."""
    active_path = skill_dir / "reference" / "troubleshooting.md"
    archive_path = skill_dir / "reference" / "troubleshooting-archive.md"

    errors: list[str] = []
    warnings: list[str] = []

    if not active_path.exists():
        errors.append(f"  active file missing: {active_path}")
        return errors, warnings, 0, 0

    active = parse_file(active_path)
    archive = parse_file(archive_path)
    all_entries = active + archive

    # Per-entry shape errors
    for e in all_entries:
        for err in e.errors:
            errors.append(f"  {e.file}:{e.line_no} entry #{e.id}: {err}")
        if not e.cause:
            errors.append(f"  {e.file}:{e.line_no} entry #{e.id}: missing Cause line")
        if not e.fix:
            errors.append(f"  {e.file}:{e.line_no} entry #{e.id}: missing Fix line")
        if not e.applies:
            errors.append(f"  {e.file}:{e.line_no} entry #{e.id}: missing Applies/Status/Last-confirmed line")

    # Duplicate IDs across combined namespace
    seen_ids: dict[int, Entry] = {}
    for e in all_entries:
        if e.id in seen_ids:
            prev = seen_ids[e.id]
            errors.append(
                f"  duplicate ID #{e.id}: {prev.file}:{prev.line_no} vs {e.file}:{e.line_no}"
            )
        else:
            seen_ids[e.id] = e

    # IDs ascending within each section of each file. The file is
    # intentionally organised by failure surface (Install / Static lint /
    # Op smoke / DB / ... / Odoo 19 / Planning); IDs are monotonic within
    # a section but new entries land in their surface's section, so
    # cross-section ordering is not monotonic by design.
    for entries_in_file in (active, archive):
        last_id_by_section: dict[str, int] = {}
        for e in entries_in_file:
            last_id = last_id_by_section.get(e.section, 0)
            if e.id <= last_id:
                section_label = f" within section '{e.section}'" if e.section else ""
                warnings.append(
                    f"  {e.file}:{e.line_no} entry #{e.id} not in ascending order{section_label} (previous was #{last_id})"
                )
            last_id_by_section[e.section] = e.id

    # Soft caps on active file
    line_count = sum(1 for _ in active_path.read_text(encoding="utf-8").splitlines())
    if line_count > ACTIVE_LINE_CAP:
        warnings.append(
            f"  active file is {line_count} lines (cap {ACTIVE_LINE_CAP}) — prune or archive entries"
        )
    if len(active) > ACTIVE_ENTRY_CAP:
        warnings.append(
            f"  active file has {len(active)} entries (cap {ACTIVE_ENTRY_CAP}) — prune or archive"
        )

    # Archive candidates: fixed for 90+ days in the active file
    today = date.today()
    for e in active:
        if e.status.startswith("fixed "):
            try:
                fixed_on = datetime.strptime(e.status[len("fixed ") :].strip(), "%Y-%m-%d").date()
            except ValueError:
                errors.append(
                    f"  {e.file}:{e.line_no} entry #{e.id}: malformed fixed date in '{e.status}'"
                )
                continue
            age = (today - fixed_on).days
            if age >= ARCHIVE_CANDIDATE_DAYS:
                warnings.append(
                    f"  active #{e.id} is fixed for {age} days "
                    f"(threshold {ARCHIVE_CANDIDATE_DAYS}) — move to archive"
                )

    # Last-confirmed date sanity (must be parseable)
    for e in all_entries:
        if not e.last_confirmed:
            continue
        try:
            datetime.strptime(e.last_confirmed, "%Y-%m-%d")
        except ValueError:
            errors.append(
                f"  {e.file}:{e.line_no} entry #{e.id}: malformed Last confirmed '{e.last_confirmed}'"
            )

    # Duplicate-symptom heuristic
    normalised: dict[str, Entry] = {}
    for e in all_entries:
        key = re.sub(r"[^a-z0-9 ]", "", e.heading.lower()).strip()
        key = re.sub(r"\s+", " ", key)
        if key in normalised:
            prev = normalised[key]
            warnings.append(
                f"  near-duplicate headings: #{prev.id} ({prev.file}) and #{e.id} ({e.file}) — consider merging"
            )
        else:
            normalised[key] = e

    return errors, warnings, len(active), line_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None, help="skills/ root override")
    parser.add_argument(
        "--skill", type=str, default=None,
        help="Skill name (e.g., odoo-plan-development). Default: lint every skill with a troubleshooting file."
    )
    parser.add_argument("--strict", action="store_true", help="warnings → errors")
    args = parser.parse_args()

    skills_root = args.root or find_skills_root(Path(__file__).parent)
    if not skills_root:
        print("ERROR: could not find skills/ root (no _shared/principles.md sibling)")
        return 2

    if args.skill:
        skill_dir = skills_root / args.skill
        if not skill_dir.is_dir():
            print(f"ERROR: skill not found: {skill_dir}")
            return 2
        skill_dirs = [skill_dir]
    else:
        skill_dirs = discover_skills_with_troubleshooting(skills_root)
        if not skill_dirs:
            print(f"No skills with troubleshooting files found under {skills_root}")
            return 0

    overall_errors = 0
    overall_warnings = 0

    for skill_dir in skill_dirs:
        active_path = skill_dir / "reference" / "troubleshooting.md"
        archive_path = skill_dir / "reference" / "troubleshooting-archive.md"

        # Count for the active file (so we can show even when missing)
        active_entries = parse_file(active_path) if active_path.exists() else []
        archive_entries = parse_file(archive_path) if archive_path.exists() else []
        line_count = sum(1 for _ in active_path.read_text(encoding="utf-8").splitlines()) if active_path.exists() else 0

        print(f"\n=== {skill_dir.name} ===")
        print(f"Active:  {len(active_entries)} entries, {line_count} lines  ({active_path.relative_to(skills_root)})")
        print(f"Archive: {len(archive_entries)} entries  ({archive_path.relative_to(skills_root) if archive_path.exists() else '(none)'})")
        combined_ids = [e.id for e in active_entries + archive_entries]
        print(f"Combined ID range: 1..{max(combined_ids, default=0)}")

        errors, warnings, _, _ = lint_skill(skill_dir)

        if errors:
            print(f"\nERRORS ({len(errors)}):")
            for line in errors:
                print(line)
            overall_errors += len(errors)

        if warnings:
            print(f"\nWARNINGS ({len(warnings)}):")
            for line in warnings:
                print(line)
            overall_warnings += len(warnings)

        if not errors and not warnings:
            print("clean")

    if overall_errors:
        return 2
    if overall_warnings and args.strict:
        return 2
    if overall_warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
