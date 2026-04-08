"""
state_bundle.py — Portable state transfer for Cognitive Architecture.

Export all evolving state into a single tarball for transfer between machines.
Import a bundle to resume exactly where the previous session left off.

Usage:
    python state_bundle.py export              # → state_YYYYMMDD_HHMMSS.tar.gz
    python state_bundle.py export my_run.tar.gz
    python state_bundle.py import state_20260407_185100.tar.gz
    python state_bundle.py status              # show what's in the current state
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# What constitutes "state" — everything the system needs to resume
# ---------------------------------------------------------------------------

AGENT_DIR = Path(__file__).parent

# Files and directories that contain evolving state
STATE_ITEMS = [
    # Core configuration (evolves during experiments)
    "constitution.yaml",

    # Agent state directory
    ".agent/",

    # Experiment logs and history
    "experiments.tsv",

    # Benchmark definitions (may have been extended during runs)
    "benchmarks/",

    # Agent population configs (evolution state)
    "agent_configs/",

    # Skills learned during runs (Hermes-style)
    "skills/",

    # Pending approval queue
    ".agent/pending_approvals.jsonl",
]

# Files to NEVER include (security, large binaries, etc.)
EXCLUDE_PATTERNS = [
    "*.pyc",
    "__pycache__",
    ".venv",
    "*.egg-info",
    ".git",
    "node_modules",
    # Don't bundle the model weights
    "*.bin",
    "*.gguf",
    "*.safetensors",
]


def _should_exclude(path: Path) -> bool:
    """Check if a path matches any exclusion pattern."""
    name = path.name
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*."):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_state(output_path: str | None = None) -> Path:
    """Bundle all evolving state into a portable tarball."""
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"state_{timestamp}.tar.gz"

    output = Path(output_path)
    if output.exists():
        print(f"[Error] Output file already exists: {output}")
        sys.exit(1)

    # Collect manifest of what we're bundling
    manifest = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "hostname": os.uname().nodename if hasattr(os, "uname") else os.environ.get("COMPUTERNAME", "unknown"),
        "items": [],
    }

    items_found = []
    for item_pattern in STATE_ITEMS:
        item_path = AGENT_DIR / item_pattern.rstrip("/")
        if item_path.exists():
            items_found.append((item_pattern, item_path))
            if item_path.is_dir():
                file_count = sum(1 for _ in item_path.rglob("*") if _.is_file() and not _should_exclude(_))
                total_size = sum(
                    f.stat().st_size for f in item_path.rglob("*")
                    if f.is_file() and not _should_exclude(f)
                )
                manifest["items"].append({
                    "path": item_pattern,
                    "type": "directory",
                    "file_count": file_count,
                    "total_bytes": total_size,
                })
            else:
                manifest["items"].append({
                    "path": item_pattern,
                    "type": "file",
                    "total_bytes": item_path.stat().st_size,
                })

    if not items_found:
        print("[Warning] No state items found. Is this the right directory?")
        sys.exit(1)

    # Write manifest to temp file
    manifest_path = AGENT_DIR / ".state_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Create tarball
    print(f"[Export] Creating state bundle: {output}")
    with tarfile.open(str(output), "w:gz") as tar:
        # Add manifest first
        tar.add(str(manifest_path), arcname=".state_manifest.json")

        for item_pattern, item_path in items_found:
            if item_path.is_dir():
                for child in item_path.rglob("*"):
                    if child.is_file() and not _should_exclude(child):
                        arcname = str(child.relative_to(AGENT_DIR))
                        tar.add(str(child), arcname=arcname)
                        print(f"  + {arcname}")
            else:
                arcname = str(item_path.relative_to(AGENT_DIR))
                tar.add(str(item_path), arcname=arcname)
                print(f"  + {arcname}")

    # Cleanup temp manifest
    manifest_path.unlink(missing_ok=True)

    file_size = output.stat().st_size
    print(f"[Export] ✓ Bundle created: {output} ({file_size:,} bytes)")
    print(f"[Export]   Items: {len(items_found)}")
    print(f"[Export]   Transfer this file to the target machine, then run:")
    print(f"[Export]   python state_bundle.py import {output.name}")

    return output


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def import_state(bundle_path: str, force: bool = False) -> None:
    """Restore state from a portable bundle."""
    bundle = Path(bundle_path)
    if not bundle.exists():
        print(f"[Error] Bundle not found: {bundle}")
        sys.exit(1)

    # Read manifest from bundle
    with tarfile.open(str(bundle), "r:gz") as tar:
        try:
            manifest_member = tar.getmember(".state_manifest.json")
            f = tar.extractfile(manifest_member)
            if f:
                manifest = json.loads(f.read().decode("utf-8"))
            else:
                manifest = {}
        except KeyError:
            manifest = {"version": 0, "items": []}

    print(f"[Import] Bundle: {bundle.name}")
    print(f"[Import] Created: {manifest.get('created_at', 'unknown')}")
    print(f"[Import] Source:  {manifest.get('hostname', 'unknown')}")
    print(f"[Import] Items:   {len(manifest.get('items', []))}")

    # Check for existing state that would be overwritten
    conflicts = []
    for item in manifest.get("items", []):
        existing = AGENT_DIR / item["path"].rstrip("/")
        if existing.exists():
            conflicts.append(item["path"])

    if conflicts and not force:
        print(f"\n[Warning] The following items already exist and will be OVERWRITTEN:")
        for c in conflicts:
            print(f"  ⚠ {c}")
        print()

        # Create automatic backup
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"state_backup_{backup_timestamp}.tar.gz"
        print(f"[Import] Creating automatic backup first: {backup_name}")
        export_state(backup_name)
        print()

    # Extract
    print(f"[Import] Extracting to {AGENT_DIR}...")
    with tarfile.open(str(bundle), "r:gz") as tar:
        # Security: check for path traversal
        for member in tar.getmembers():
            if member.name.startswith("/") or ".." in member.name:
                print(f"[Error] Unsafe path in bundle: {member.name}")
                sys.exit(1)

        # Extract everything except the manifest
        for member in tar.getmembers():
            if member.name == ".state_manifest.json":
                continue
            tar.extract(member, path=str(AGENT_DIR))
            print(f"  ← {member.name}")

    print(f"[Import] ✓ State restored successfully.")
    print(f"[Import]   The experiment loop will auto-resume from the last checkpoint.")


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def show_status() -> None:
    """Show what state currently exists."""
    print(f"[Status] Agent directory: {AGENT_DIR}")
    print()

    for item_pattern in STATE_ITEMS:
        item_path = AGENT_DIR / item_pattern.rstrip("/")
        if item_path.exists():
            if item_path.is_dir():
                file_count = sum(1 for _ in item_path.rglob("*") if _.is_file())
                total_size = sum(f.stat().st_size for f in item_path.rglob("*") if f.is_file())
                print(f"  ✓ {item_pattern:<40} {file_count:>4} files, {total_size:>10,} bytes")
            else:
                size = item_path.stat().st_size
                mtime = datetime.fromtimestamp(item_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                print(f"  ✓ {item_pattern:<40} {size:>10,} bytes  (modified: {mtime})")
        else:
            print(f"  ✗ {item_pattern:<40} (not found)")

    # Show experiment count if log exists
    tsv_path = AGENT_DIR / "experiments.tsv"
    if tsv_path.exists():
        lines = tsv_path.read_text(encoding="utf-8").strip().split("\n")
        # Subtract header line
        exp_count = max(0, len(lines) - 1)
        print(f"\n  Experiments logged: {exp_count}")

    # Show pending approvals
    approvals_path = AGENT_DIR / ".agent" / "pending_approvals.jsonl"
    if approvals_path.exists():
        lines = approvals_path.read_text(encoding="utf-8").strip().split("\n")
        pending = len([l for l in lines if l.strip()])
        print(f"  Pending approvals:  {pending}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Portable state transfer for Cognitive Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python state_bundle.py export                    # Create timestamped bundle
  python state_bundle.py export my_checkpoint.tar.gz  # Named bundle
  python state_bundle.py import state_20260407.tar.gz  # Restore state
  python state_bundle.py status                    # Show current state
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Export
    export_parser = subparsers.add_parser("export", help="Bundle state for transfer")
    export_parser.add_argument("output", nargs="?", default=None, help="Output filename (default: auto-timestamped)")

    # Import
    import_parser = subparsers.add_parser("import", help="Restore state from bundle")
    import_parser.add_argument("bundle", help="Path to .tar.gz bundle")
    import_parser.add_argument("--force", action="store_true", help="Skip backup prompt")

    # Status
    subparsers.add_parser("status", help="Show current state")

    args = parser.parse_args()

    if args.command == "export":
        export_state(args.output)
    elif args.command == "import":
        import_state(args.bundle, force=args.force)
    elif args.command == "status":
        show_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
