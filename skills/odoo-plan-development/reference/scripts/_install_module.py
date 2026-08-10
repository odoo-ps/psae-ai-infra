"""Stage-2 install/upgrade runner.

Wraps `odoo-bin -i <module>` (or `-u` if already installed), captures the log,
and reports any ERROR/WARNING lines that suggest the install didn't really
succeed even though the process exited 0.

Usage:
    python3 _install_module.py \\
        --venv-python ./v19/odoo/.venv/bin/python \\
        --odoo-bin ./v19/odoo/odoo-bin \\
        --conf <instance>/odoo.conf \\
        --db <db_name> \\
        --module <module>
"""
import argparse
import re
import subprocess
import sys


SUSPICIOUS_PATTERNS = [
    re.compile(r"\bERROR\b", re.IGNORECASE),
    re.compile(r"\bTraceback\b"),
    re.compile(r"Failed to load"),
    re.compile(r"could not load"),
    re.compile(r"Module .* not found"),
    re.compile(r"odoo\.exceptions\."),
]


def is_installed(venv_python: str, odoo_bin: str, conf: str, db: str, module: str) -> bool:
    """Probe whether the module is already installed in the DB."""
    py = (
        "import sys; "
        f"mod = env['ir.module.module'].search([('name','=','{module}')], limit=1); "
        "sys.stdout.write('STATE:' + (mod.state or 'absent'))"
    )
    proc = subprocess.run(
        [venv_python, odoo_bin, "shell", "-c", conf, "-d", db,
         "--no-http", "--stop-after-init"],
        input=py, text=True, capture_output=True, timeout=180,
    )
    out = proc.stdout + proc.stderr
    m = re.search(r"STATE:(\w+)", out)
    return bool(m and m.group(1) == "installed")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--venv-python", required=True)
    ap.add_argument("--odoo-bin", required=True)
    ap.add_argument("--conf", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--module", required=True)
    ap.add_argument("--force-upgrade", action="store_true",
                    help="Run -u even if the module is not yet installed")
    args = ap.parse_args()

    print(f"--- Probing install state of {args.module} on {args.db}")
    try:
        already = is_installed(args.venv_python, args.odoo_bin, args.conf, args.db, args.module)
    except Exception as e:
        print(f"FAIL: probe failed: {e}")
        return 1
    flag = "-u" if (already or args.force_upgrade) else "-i"
    print(f"  state: {'installed' if already else 'absent'}; will run {flag}")

    cmd = [args.venv_python, args.odoo_bin,
           "-c", args.conf, "-d", args.db,
           "--no-http", "--stop-after-init",
           flag, args.module]
    print(f"--- Running: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    output = proc.stdout + proc.stderr

    # Pretty-print last 80 lines
    tail = "\n".join(output.splitlines()[-80:])
    print(tail)

    flagged = []
    for line in output.splitlines():
        for p in SUSPICIOUS_PATTERNS:
            if p.search(line):
                flagged.append(line.strip())
                break

    print(f"--- Process exit code: {proc.returncode}")
    print(f"--- Suspicious lines: {len(flagged)}")
    for ln in flagged[:40]:
        print(f"  {ln}")
    if len(flagged) > 40:
        print(f"  ... ({len(flagged) - 40} more)")

    if proc.returncode != 0 or flagged:
        print(f"FAIL: install of {args.module} did not complete cleanly")
        return 1
    print(f"PASS: {args.module} {flag} succeeded on {args.db}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
