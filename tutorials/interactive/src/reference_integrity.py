"""Identify the guide's scientific sources without requiring Git history.

The checked manifest records file contents, not a moving branch name. Public
links are navigation aids; SHA-256 values identify the source bytes used here.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
MANIFEST_PATH = HERE / "reference_sources.json"
REFERENCE_PATH = HERE / "scientific_reference.json"
SOURCE_BASE = "https://github.com/dortizbarrientos/additive_channels/blob/main/"
SCIENTIFIC_SECTIONS = (
    "scalar_inheritance", "selection", "estimation", "geometry", "one_trait",
)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def scientific_payload(reference: dict) -> dict:
    """Keep every scientific value and statement, omitting source annotations.

    The baseline includes all saved draws, displayed observations, formulas,
    assumptions and calculated reference trajectories. Source URLs and the
    prose identifying their storage location can change independently.
    """
    payload = {key: copy.deepcopy(reference[key]) for key in SCIENTIFIC_SECTIONS}

    def remove_annotations(value):
        if isinstance(value, dict):
            return {
                key: remove_annotations(item)
                for key, item in value.items()
                if key not in {"source", "sources", "trajectory_provenance"}
            }
        if isinstance(value, list):
            return [remove_annotations(item) for item in value]
        return value

    return remove_annotations(payload)


def scientific_sha256(reference: dict) -> str:
    raw = json.dumps(
        scientific_payload(reference), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")
    return sha256(raw)


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def read_checked_source(path: str, manifest: dict | None = None) -> bytes:
    """Read a listed source only when its bytes match the reviewed manifest."""
    manifest = load_manifest() if manifest is None else manifest
    entries = {item["path"]: item for item in manifest["sources"]}
    if path not in entries:
        raise ValueError(f"Source is not listed in reference_sources.json: {path}")
    target = (REPO / path).resolve()
    if not target.is_relative_to(REPO.resolve()):
        raise ValueError(f"Source path leaves the repository: {path}")
    raw = target.read_bytes()
    observed = sha256(raw)
    expected = entries[path]["sha256"]
    if observed != expected:
        raise ValueError(
            f"Source hash changed: {path}\n"
            f"Expected {expected}; found {observed}.\n"
            "Review the source change and its scientific consequences before "
            "updating the manifest and rebuilding the guide."
        )
    return raw


def validate_reference(record: dict | None = None) -> dict:
    """Check source bytes, model bytes and the embedded scientific baseline."""
    manifest = load_manifest()
    record = (
        json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
        if record is None else record
    )
    sources = {item["path"]: item for item in manifest["sources"]}
    recorded = {item["path"]: item for item in record["source_manifest"]}
    if len(sources) != len(manifest["sources"]) or set(recorded) != set(sources):
        raise ValueError("The reference and manifest must list the same unique sources.")
    for path, expected in sources.items():
        read_checked_source(path, manifest)
        if recorded[path]["sha256"] != expected["sha256"]:
            raise ValueError(f"Reference source hash does not match the manifest: {path}")
        if recorded[path]["github_url"] != SOURCE_BASE + path:
            raise ValueError(f"Reference source link does not use the public source path: {path}")
    manifest_hash = sha256(MANIFEST_PATH.read_bytes())
    if record["source_identity"]["manifest_sha256"] != manifest_hash:
        raise ValueError("The reference record was not extracted from the current manifest.")
    model_hash = sha256((HERE / "models.js").read_bytes())
    if model_hash != manifest["model_sha256"]:
        raise ValueError("models.js differs from the reviewed mathematical model.")
    science_hash = scientific_sha256(record)
    if science_hash != manifest["scientific_values_sha256"]:
        raise ValueError("Scientific values or assumptions differ from the reviewed baseline.")
    return {
        "all_checks_passed": True,
        "source_files_checked": len(sources),
        "manifest_sha256": manifest_hash,
        "model_sha256": model_hash,
        "scientific_values_sha256": science_hash,
    }
