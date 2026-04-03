#!/usr/bin/env python3
"""
cuntext validator — checks .cuntext files against the spec (v0.1)
Usage:
  python validate.py examples/greed-compute/index.cuntext
  python validate.py examples/nextjs-project/fragments/architecture.cuntext
  python validate.py examples/greed-compute/          # validate a whole directory
"""

import re
import sys
from pathlib import Path


# ── token estimation (rough: 1 token ≈ 4 chars) ─────────────────────────────

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


# ── validators ───────────────────────────────────────────────────────────────

def validate_index(path: Path, text: str) -> list[str]:
    errors = []
    warnings = []
    lines = text.splitlines()

    # Line 1: {NAME} v{VERSION}
    if not lines:
        errors.append("file is empty")
        return errors

    header_re = re.compile(r"^[A-Z][A-Z0-9_-]* v\d+(\.\d+)?$")
    if not header_re.match(lines[0]):
        errors.append(
            f"line 1: expected '{{NAME}} v{{VERSION}}' (e.g. 'MYAPI v1'), got: {lines[0]!r}"
        )

    # base= required
    if not any(l.startswith("base=") for l in lines):
        errors.append("missing required metadata key: base=")

    # goals: block required with at least one entry
    goal_re = re.compile(r"^\s{2}\S.+→.+\.cuntext$")
    in_goals = False
    goal_count = 0
    for line in lines:
        if line.strip() == "goals:":
            in_goals = True
            continue
        if in_goals:
            if line.startswith("  ") and line.strip():
                if "→" in line or "->" in line:
                    goal_count += 1
            elif line.strip() and not line.startswith(" "):
                in_goals = False

    if goal_count == 0:
        errors.append("goals: block is missing or has no entries")
    elif goal_count < 3:
        warnings.append(f"goals: block has only {goal_count} entr{'y' if goal_count == 1 else 'ies'} (recommend ≥ 3)")

    # auth-setup if auth is present
    has_auth = any(l.startswith("auth=") for l in lines)
    has_auth_setup = any(l.startswith("auth-setup=") for l in lines)
    if has_auth and not has_auth_setup:
        warnings.append("auth= is set but auth-setup= is missing — agents won't know how to get a key")

    # on-error advisory — only relevant for HTTP API contexts
    base_val = next((l.split("=", 1)[1] for l in lines if l.startswith("base=")), "")
    is_http = base_val.startswith("http")
    if is_http:
        has_on_error = any(l.startswith("on-error:") for l in lines)
        if not has_on_error:
            warnings.append("on-error: not present — agents must load errors fragment for all error handling")

    # token count
    tokens = estimate_tokens(text)
    if tokens > 300:
        warnings.append(f"index is ~{tokens} tokens (target ≤ 250) — consider trimming")
    elif tokens > 250:
        warnings.append(f"index is ~{tokens} tokens (target ≤ 250)")

    return _format_results(path, errors, warnings)


def validate_fragment(path: Path, text: str) -> list[str]:
    errors = []
    warnings = []
    lines = text.splitlines()

    if not lines:
        errors.append("file is empty")
        return errors

    # Line 1: {NAME} ...
    name_re = re.compile(r"^[A-Z][A-Z0-9_-]*(\s+\[.+\])?$")
    if not name_re.match(lines[0]):
        errors.append(
            f"line 1: expected '{{NAME}} [optional description]' in uppercase, got: {lines[0]!r}"
        )

    # at least one operation or reference block
    # operation block: "name:" (lowercase label followed by colon)
    # reference block: lines starting with HTTP status codes (e.g. "400  bad-request")
    op_re = re.compile(r"^[a-z][a-z0-9._-]*:$")
    ref_re = re.compile(r"^\d{3}\s+\S")
    has_operation = any(op_re.match(l) or ref_re.match(l) for l in lines)
    if not has_operation:
        errors.append("no operation or reference blocks found — fragment must contain at least one 'name:' block or status-code reference")

    # ex: block
    has_ex = any(l.strip() == "ex:" for l in lines)
    if not has_ex:
        warnings.append("no ex: block — agents benefit from at least one inline example")

    # deps declared if note/type references suggest other fragments
    has_deps = any(l.startswith("deps=") for l in lines)
    if not has_deps:
        warnings.append("no deps= line — if this fragment assumes another is loaded, declare it")

    # token count
    tokens = estimate_tokens(text)
    if tokens > 500:
        warnings.append(f"fragment is ~{tokens} tokens (target ≤ 400) — consider splitting by goal")
    elif tokens > 400:
        warnings.append(f"fragment is ~{tokens} tokens (target ≤ 400)")

    return _format_results(path, errors, warnings)


def _format_results(path: Path, errors: list[str], warnings: list[str]) -> list[str]:
    out = []
    for e in errors:
        out.append(f"  ERROR   {e}")
    for w in warnings:
        out.append(f"  WARN    {w}")
    return out


# ── file detection ────────────────────────────────────────────────────────────

def is_index(path: Path) -> bool:
    return path.name == "index.cuntext"


def validate_file(path: Path) -> bool:
    """Returns True if file passes (no errors)."""
    text = path.read_text(encoding="utf-8")
    if is_index(path):
        kind = "index"
        results = validate_index(path, text)
    else:
        kind = "fragment"
        results = validate_fragment(path, text)

    errors = [r for r in results if "ERROR" in r]
    warnings = [r for r in results if "WARN" in r]

    status = "PASS" if not errors else "FAIL"
    tokens = estimate_tokens(text)
    print(f"[{status}] {path}  ({kind}, ~{tokens} tokens)")
    for line in results:
        print(line)
    if results:
        print()

    return not errors


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    targets = [Path(arg) for arg in sys.argv[1:]]
    files: list[Path] = []

    for target in targets:
        if target.is_dir():
            files.extend(sorted(target.rglob("*.cuntext")))
        elif target.is_file():
            files.append(target)
        else:
            print(f"not found: {target}", file=sys.stderr)
            sys.exit(1)

    if not files:
        print("no .cuntext files found")
        sys.exit(1)

    passed = sum(1 for f in files if validate_file(f))
    total = len(files)
    failed = total - passed

    print(f"{'─' * 40}")
    print(f"{passed}/{total} passed", end="")
    if failed:
        print(f"  ({failed} failed)")
        sys.exit(1)
    else:
        print()


if __name__ == "__main__":
    main()
