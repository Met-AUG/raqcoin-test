#!/usr/bin/env python3
"""
Batch-rename all files whose basename contains 'raqcoin' to replace that
substring with 'raqcoin', and update references to those filenames across
text files in the repository.

Usage:
  - Dry run (default):
      python tools/rename_raqcoin_to_raqcoin.py
  - Apply changes:
      python tools/rename_raqcoin_to_raqcoin.py --apply

Notes:
  - Only basenames are renamed (directories are not renamed).
  - Only references to the exact old basenames are replaced in file contents.
  - Binary files are not modified.
  - A two-phase rename is used to avoid name collisions on case-insensitive FS.
"""
from __future__ import annotations
import argparse
import os
import sys
import uuid
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable

REPO_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
CURRENT_SCRIPT_PATH = os.path.abspath(__file__)

# Conservative list of text-like extensions; we will also try a lenient
# UTF-8 decode to catch other plain text files.
TEXT_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".ipp",
    ".m", ".mm",
    ".pro", ".pri", ".pri.in", ".qrc", ".rc", ".ui",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".conf",
    ".txt", ".md", ".rst", ".csv",
    ".py", ".sh", ".bash", ".zsh", ".ps1",
    ".ts",  # Qt translation (XML)
    ".patch", ".diff",
    ".desktop", ".protocol", ".service",
    ".nsi", ".xml",
    ".mk", ".make", ".am", ".ac",
    ".plist",
    ".gradle", ".properties",
    ".clang-format", ".editorconfig",
    ".qss",
    "",  # files without extension (e.g., Makefile)
}

# Obvious binary extensions to skip when considering reference updates
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".icns",
    ".psd", ".tiff", ".tif", ".pdf",
    ".xpm",  # often C-like text, but we don't need to edit its content
    ".svg",  # technically text, but treat as asset; references in .qrc will be updated
    ".a", ".o", ".so", ".dylib", ".dll", ".lib", ".exe",
    ".db", ".sqlite", ".bin",
}

# Filenames that are text even if no extension
ALWAYS_TEXT_FILENAMES = {
    "Makefile", "makefile", "GNUmakefile", "Dockerfile",
}

EXCLUDED_DIRS = {".git", ".idea", ".vscode", "node_modules", "build", "dist", "out", "obj", "obj-test"}

@dataclass
class Plan:
    file_renames: List[Tuple[str, str]]  # (old_abs, new_abs)
    content_replacements: Dict[str, str]  # old_basename -> new_basename


def is_text_like(path: str) -> bool:
    base = os.path.basename(path)
    if base in ALWAYS_TEXT_FILENAMES:
        return True
    ext = os.path.splitext(base)[1]
    if ext in BINARY_EXTENSIONS:
        return False
    if ext in TEXT_EXTENSIONS:
        return True
    # Fallback heuristic: small files or ones that decode to mostly printable
    try:
        with open(path, "rb") as f:
            chunk = f.read(4096)
        if b"\x00" in chunk:
            return False
        # Try decoding as UTF-8 with replacement
        _ = chunk.decode("utf-8", errors="ignore")
        return True
    except Exception:
        return False


def walk_files(root: str) -> Iterable[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        # prune excluded dirs in-place
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def build_plan(root: str) -> Plan:
    # Identify files whose basenames contain 'raqcoin'
    candidates: List[str] = []
    for path in walk_files(root):
        base = os.path.basename(path)
        # Skip this script itself to avoid self-renaming
        if os.path.abspath(path) == CURRENT_SCRIPT_PATH:
            continue
        if "raqcoin" in base:
            candidates.append(path)
    # Build rename mapping and verify uniqueness
    file_renames: List[Tuple[str, str]] = []
    content_replacements: Dict[str, str] = {}
    seen_targets: set[str] = set()
    for old_abs in sorted(candidates):
        old_base = os.path.basename(old_abs)
        new_base = old_base.replace("raqcoin", "raqcoin")
        new_abs = os.path.join(os.path.dirname(old_abs), new_base)
        file_renames.append((old_abs, new_abs))
        content_replacements[old_base] = new_base
        if new_abs in seen_targets:
            raise RuntimeError(f"Target collision detected: {new_abs}")
        seen_targets.add(new_abs)
    return Plan(file_renames=file_renames, content_replacements=content_replacements)


def apply_two_phase_renames(renames: List[Tuple[str, str]]) -> None:
    nonce = uuid.uuid4().hex[:8]
    temp_pairs: List[Tuple[str, str]] = []
    # Phase 1: move to temporary names to avoid collisions
    for old_abs, new_abs in renames:
        dirn = os.path.dirname(old_abs)
        old_base = os.path.basename(old_abs)
        temp_base = old_base.replace("raqcoin", f"raqcoin__tmp__{nonce}")
        temp_abs = os.path.join(dirn, temp_base)
        if not os.path.exists(old_abs):
            # Already moved? Skip
            continue
        if os.path.exists(temp_abs):
            raise RuntimeError(f"Temporary path already exists: {temp_abs}")
        os.rename(old_abs, temp_abs)
        temp_pairs.append((temp_abs, new_abs))
    # Phase 2: move temporary to final names
    for temp_abs, new_abs in temp_pairs:
        final_dir = os.path.dirname(new_abs)
        os.makedirs(final_dir, exist_ok=True)
        if os.path.exists(new_abs):
            raise RuntimeError(f"Final target already exists: {new_abs}")
        os.rename(temp_abs, new_abs)


def update_references(root: str, mapping: Dict[str, str], dry_run: bool, brand_all: bool = False) -> Tuple[int, int]:
    files_scanned = 0
    files_modified = 0
    for path in walk_files(root):
        # Skip files we just renamed? Not necessary, but process all text files
        if not is_text_like(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue
        original = content
        for old_base, new_base in mapping.items():
            if old_base in content:
                content = content.replace(old_base, new_base)
        # Optional: global brand replacement inside text files
        if brand_all:
            # Preserve upstream copyright headers, external URLs, protocol-level strings, etc.
            # that would cause forks or break external references if changed.
            # Do a line-wise replacement with comprehensive skip conditions.
            lines = content.splitlines(True)  # keepends=True
            
            def should_skip_line(line: str) -> bool:
                """Return True if this line should NOT have brand replacements applied."""
                low = line.lower()
                
                # 1. Copyright headers mentioning developers
                if "copyright" in low and "developer" in low:
                    return True
                
                # 2. External HTTP(S) URLs (preserve external links)
                if "http://" in low or "https://" in low:
                    # Allow replacement in comments explaining local code, but skip actual URLs
                    # Simple heuristic: if line has a domain-like pattern, skip it
                    if any(domain in low for domain in [".org", ".com", ".net", ".io", ".edu", ".gov"]):
                        return True
                
                # 3. Message signing protocol string (critical for compatibility)
                # "Abcmint Signed Message:\n" must stay unchanged
                if "signed message" in low:
                    return True
                
                # 4. URI scheme declarations (abcmint: protocol)
                # Lines like: const QString ABCMINT_IPC_PREFIX("abcmint:");
                # or parseAbcmintURI, or "abcmint:" in URI examples
                if "abcmint:" in line or "abcmint://" in line:
                    return True
                
                # 5. Data directory path hints in comments or help text
                # e.g., "~/.abcmint" or "Application Support/abc" references
                # Check for filesystem path patterns
                if any(pattern in line for pattern in ["~/.abc", "/.abc", "\\abc", "/abc", "Application Support/abc"]):
                    return True
                
                # 6. Git/GitHub URLs and repository references
                if "github.com" in low or "sourceforge.net" in low:
                    return True
                
                return False

            brand_variants = (
                ("raqcoin", "raqcoin"),
                ("Raqcoin", "Raqcoin"),
                ("RAQCOIN", "RAQCOIN"),
            )
            new_lines = []
            for ln in lines:
                if should_skip_line(ln):
                    new_lines.append(ln)
                    continue
                new_ln = ln
                for old, new in brand_variants:
                    if old in new_ln:
                        new_ln = new_ln.replace(old, new)
                new_lines.append(new_ln)
            content = "".join(new_lines)
        # Special handling: .rc resource identifier 'raqcoin' (without extension)
        # Only replace the standalone identifier at line start or preceded by whitespace
        # to avoid over-broad symbol renames elsewhere.
        if path.endswith('.rc'):
            # Pattern: start of line optional whitespace then 'raqcoin' then whitespace and (ICON|BITMAP|PNG|JPG)
            pattern = re.compile(r'^(\s*)raqcoin(\s+(ICON|BITMAP|PNG|JPG))', re.MULTILINE)
            def repl(m: re.Match) -> str:
                return f"{m.group(1)}raqcoin{m.group(2)}"
            content = pattern.sub(repl, content)
        files_scanned += 1
        if content != original:
            files_modified += 1
            if not dry_run:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
    return files_scanned, files_modified


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Rename files containing 'raqcoin' to 'raqcoin' and update references.")
    parser.add_argument("--apply", action="store_true", help="Apply changes. Without this flag, runs in dry-run mode.")
    parser.add_argument("--brand-all", action="store_true", help="Also replace 'raqcoin' brand tokens in all text files (identifiers, strings, docs) with 'raqcoin' (case-aware).")
    parser.add_argument("--root", default=REPO_ROOT, help="Repository root (default: project root)")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"Error: root not found: {root}", file=sys.stderr)
        return 2

    plan = build_plan(root)
    print(f"Discovered {len(plan.file_renames)} files to rename containing 'raqcoin'.")

    # Print planned renames
    for old_abs, new_abs in plan.file_renames:
        rel_old = os.path.relpath(old_abs, root)
        rel_new = os.path.relpath(new_abs, root)
        print(f"  {rel_old} -> {rel_new}")

    # Update references (dry-run or apply)
    action_phrase = "and brand tokens " if args.brand_all else ""
    print(f"Scanning and updating references to renamed basenames {action_phrase}across text files...")
    scanned, modified = update_references(root, plan.content_replacements, dry_run=not args.apply, brand_all=args.brand_all)
    print(f"Text files scanned: {scanned}, files with changes: {modified}")

    if not args.apply:
        print("Dry-run complete. Re-run with --apply to perform renames and write changes.")
        return 0

    # Perform two-phase renames only when applying
    print("Performing two-phase safe renames...")
    apply_two_phase_renames(plan.file_renames)
    print("Renames complete.")

    # After renames, run references update once more to catch any paths emitted by tooling
    print("Re-scanning references after rename to ensure consistency...")
    scanned2, modified2 = update_references(root, plan.content_replacements, dry_run=False, brand_all=args.brand_all)
    print(f"Re-scan complete. Text files scanned: {scanned2}, files updated: {modified2}")

    print("All done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
