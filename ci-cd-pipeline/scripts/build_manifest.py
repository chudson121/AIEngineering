#!/usr/bin/env python3
"""
build_manifest.py
=================
Builds the effective release manifest (RA Section 3 & 4.1).
Hashes all prompt templates and tool schemas; records model routing config,
corpus versions, and evaluator versions into a single JSON manifest.

Usage:
  python scripts/build_manifest.py \
    --git-sha  <sha> \
    --git-ref  <ref> \
    --output   release-manifest.json
"""

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import yaml
from rich.console import Console

console = Console()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_directory(directory: Path, glob: str = "**/*") -> dict[str, str]:
    hashes = {}
    if not directory.exists():
        return hashes
    for p in sorted(directory.glob(glob)):
        if p.is_file():
            hashes[str(p.relative_to(directory))] = sha256_file(p)
    return hashes


def bundle_hash(hashes: dict[str, str]) -> str:
    combined = "".join(f"{k}:{v}" for k, v in sorted(hashes.items()))
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-sha",  required=True)
    ap.add_argument("--git-ref",  required=True)
    ap.add_argument("--output",   required=True)
    args = ap.parse_args()

    # Hash prompt templates
    prompt_hashes = hash_directory(Path("prompts"), "**/*.jinja2")
    prompt_hashes.update(hash_directory(Path("prompts"), "**/*.yaml"))

    # Hash tool schemas
    tool_hashes = hash_directory(Path("tools"), "**/*.json")

    # Read model routing config
    model_routing = {}
    routing_path = Path("config/model-routing.yaml")
    if routing_path.exists():
        with open(routing_path) as f:
            model_routing = yaml.safe_load(f)

    manifest = {
        "schema_version":    "1.0",
        "timestamp":         datetime.now(timezone.utc).isoformat(),
        "git_sha":           args.git_sha,
        "git_ref":           args.git_ref,
        "cloud_provider":    os.getenv("CLOUD_PROVIDER", "unset"),
        "prompt_hash":       bundle_hash(prompt_hashes),
        "prompt_files":      prompt_hashes,
        "tool_schema_hash":  bundle_hash(tool_hashes),
        "tool_schema_files": tool_hashes,
        "model_routing": {
            "default_provider": model_routing.get("default_provider", "unset"),
            "judge_provider":   model_routing.get("judge_provider", "unset"),
        },
        "evaluator_version": os.getenv("EVALUATOR_VERSION", "latest"),
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2)

    console.print(f"[green]✅ Release manifest written → {out}[/]")
    console.print(f"   prompt_hash:      {manifest['prompt_hash']}")
    console.print(f"   tool_schema_hash: {manifest['tool_schema_hash']}")


if __name__ == "__main__":
    main()
