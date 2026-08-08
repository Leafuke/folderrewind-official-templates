from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
PRESETS_DIR = ROOT / "presets"
INDEX_PATH = PRESETS_DIR / "index.json"
SHARE_CODE_RE = re.compile(r"^[A-HJ-NP-Z2-9]{5}$")


def load_json(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def sha256_hex(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def validate_source(source: object, path: pathlib.Path, errors: list[str]) -> tuple[str, str] | None:
    if not isinstance(source, dict):
        errors.append(f"{path.name}: discovery source must be an object")
        return None
    kind = source.get("Kind")
    if kind == 0:
        rules = source.get("PathRules")
        if not isinstance(rules, list) or not rules:
            errors.append(f"{path.name}: InlinePathRules source has no path rules")
        return None
    if kind == 1:
        provider_id = str(source.get("ProviderId") or "").strip()
        definition_id = str(source.get("DefinitionId") or "").strip()
        if not provider_id or not definition_id:
            errors.append(f"{path.name}: ProviderReference requires ProviderId and DefinitionId")
            return None
        return provider_id.lower(), definition_id.lower()
    errors.append(f"{path.name}: unsupported discovery source kind {kind!r}")
    return None


def validate_preset(
    path: pathlib.Path,
    share_ids: set[str],
    share_codes: set[str],
    recommendations: dict[tuple[str, str], str],
) -> tuple[list[str], dict | None]:
    errors: list[str] = []
    envelope = load_json(path)
    if envelope.get("Magic") != "FolderRewindBackupPreset" or envelope.get("SchemaVersion") != "2.0":
        errors.append(f"{path.name}: invalid Backup Preset V2 envelope")
    preset = envelope.get("Preset")
    if not isinstance(preset, dict):
        errors.append(f"{path.name}: missing Preset object")
        return errors, None

    share_id = str(preset.get("ShareId") or "").strip()
    share_code = str(preset.get("ShareCode") or "").strip().upper()
    if not share_id:
        errors.append(f"{path.name}: missing ShareId")
    elif share_id.lower() in share_ids:
        errors.append(f"{path.name}: duplicate ShareId {share_id}")
    else:
        share_ids.add(share_id.lower())
    if not SHARE_CODE_RE.fullmatch(share_code) or path.name != f"{share_code}.frpreset.json":
        errors.append(f"{path.name}: invalid or mismatched ShareCode")
    elif share_code in share_codes:
        errors.append(f"{path.name}: duplicate ShareCode {share_code}")
    else:
        share_codes.add(share_code)

    sources = preset.get("DiscoverySources")
    provider_keys: list[tuple[str, str]] = []
    if not isinstance(sources, list) or not sources:
        errors.append(f"{path.name}: at least one DiscoverySource is required")
    else:
        for source in sources:
            key = validate_source(source, path, errors)
            if key:
                provider_keys.append(key)

    required_plugins = {
        str(item).strip().lower()
        for item in preset.get("RequiredPluginIds") or []
        if str(item).strip()
    }
    for provider_id, _ in provider_keys:
        if provider_id.startswith("com.folderrewind.") and provider_id not in required_plugins:
            errors.append(f"{path.name}: plugin provider {provider_id} must be declared in RequiredPluginIds")

    if bool(preset.get("IsRecommended")):
        for key in provider_keys:
            if key in recommendations:
                errors.append(
                    f"{path.name}: recommended preset conflicts with {recommendations[key]} for {key[0]}/{key[1]}"
                )
            else:
                recommendations[key] = path.name
    return errors, preset


def validate_index(presets: dict[str, tuple[pathlib.Path, dict]]) -> list[str]:
    errors: list[str] = []
    if not INDEX_PATH.exists():
        return ["presets/index.json is missing"]
    document = load_json(INDEX_PATH)
    if document.get("magic") != "FolderRewindBackupPresetIndex" or document.get("schemaVersion") != "2.0":
        errors.append("presets/index.json: invalid magic or schemaVersion")
    entries = document.get("presets")
    if not isinstance(entries, list):
        return errors + ["presets/index.json: presets must be an array"]

    indexed_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("presets/index.json: entry must be an object")
            continue
        share_id = str(entry.get("shareId") or "").strip().lower()
        if share_id in indexed_ids:
            errors.append(f"presets/index.json: duplicate ShareId {share_id}")
        indexed_ids.add(share_id)
        item = presets.get(share_id)
        if item is None:
            errors.append(f"presets/index.json: unknown ShareId {share_id}")
            continue
        path, preset = item
        if entry.get("contentPath") != f"presets/{path.name}":
            errors.append(f"presets/index.json: wrong contentPath for {share_id}")
        if str(entry.get("sha256") or "").upper() != sha256_hex(path):
            errors.append(f"presets/index.json: hash mismatch for {share_id}")
        if str(entry.get("shareCode") or "").upper() != str(preset.get("ShareCode") or "").upper():
            errors.append(f"presets/index.json: ShareCode mismatch for {share_id}")

    missing = set(presets) - indexed_ids
    for share_id in sorted(missing):
        errors.append(f"presets/index.json: missing preset {share_id}")
    return errors


def main() -> int:
    all_errors: list[str] = []
    share_ids: set[str] = set()
    share_codes: set[str] = set()
    recommendations: dict[tuple[str, str], str] = {}
    presets: dict[str, tuple[pathlib.Path, dict]] = {}
    for path in sorted(PRESETS_DIR.glob("*.frpreset.json")):
        errors, preset = validate_preset(path, share_ids, share_codes, recommendations)
        all_errors.extend(errors)
        if preset is not None:
            share_id = str(preset.get("ShareId") or "").strip().lower()
            if share_id:
                presets[share_id] = (path, preset)
    all_errors.extend(validate_index(presets))

    if all_errors:
        print("Backup Preset V2 validation failed:", file=sys.stderr)
        for error in all_errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Backup Preset V2 validation passed for {len(presets)} preset(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
