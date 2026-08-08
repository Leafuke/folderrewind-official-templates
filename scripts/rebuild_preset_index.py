from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone


ROOT = pathlib.Path(__file__).resolve().parents[1]
PRESETS_DIR = ROOT / "presets"
INDEX_PATH = PRESETS_DIR / "index.json"


def sha256_hex(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_json(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def provider_matches(preset: dict) -> list[dict]:
    matches: list[dict] = []
    for source in preset.get("DiscoverySources") or []:
        if source.get("Kind") != 1:
            continue
        provider_id = str(source.get("ProviderId") or "").strip()
        definition_id = str(source.get("DefinitionId") or "").strip()
        if provider_id and definition_id:
            matches.append({
                "providerId": provider_id,
                "definitionId": definition_id,
                "externalIds": source.get("ExternalIds") or {},
            })
    return matches


def build_entry(path: pathlib.Path) -> dict:
    envelope = load_json(path)
    preset = envelope["Preset"]
    return {
        "shareId": preset["ShareId"],
        "shareCode": preset["ShareCode"],
        "name": preset.get("Name", ""),
        "author": preset.get("Author", ""),
        "description": preset.get("Description", ""),
        "gameName": preset.get("GameName", ""),
        "steamAppId": preset.get("SteamAppId"),
        "version": preset.get("Version", "1.0"),
        "updatedUtc": preset.get("UpdatedUtc") or envelope.get("ExportedAtUtc"),
        "baseConfigType": preset.get("BaseConfigType", "Default"),
        "requiredPluginIds": preset.get("RequiredPluginIds") or [],
        "contentPath": f"presets/{path.name}",
        "sha256": sha256_hex(path),
        "matches": provider_matches(preset),
        "isRecommended": bool(preset.get("IsRecommended", False)),
        "isDisabled": False,
    }


def main() -> int:
    entries = [build_entry(path) for path in sorted(PRESETS_DIR.glob("*.frpreset.json"))]
    entries.sort(key=lambda item: (
        (item.get("gameName") or "").lower(),
        (item.get("name") or "").lower(),
        item.get("shareId") or "",
    ))
    document = {
        "magic": "FolderRewindBackupPresetIndex",
        "schemaVersion": "2.0",
        "generatedAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "presets": entries,
    }
    INDEX_PATH.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Rebuilt {INDEX_PATH} with {len(entries)} preset(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
