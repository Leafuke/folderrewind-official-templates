from __future__ import annotations

import copy
import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / "templates"
PRESETS_DIR = ROOT / "presets"
MINE_REWIND_ID = "com.folderrewind.minerewind"
MINECRAFT_DEFINITION_ID = "minecraft-java"


def load_json(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def inline_source(path_rules: list[dict]) -> dict:
    return {
        "Kind": 0,
        "ProviderId": "",
        "DefinitionId": "",
        "PathRules": copy.deepcopy(path_rules),
        "ExternalIds": {},
        "Properties": {},
    }


def mine_rewind_source() -> dict:
    return {
        "Kind": 1,
        "ProviderId": MINE_REWIND_ID,
        "DefinitionId": MINECRAFT_DEFINITION_ID,
        "PathRules": [],
        "ExternalIds": {},
        "Properties": {},
    }


def migrate(path: pathlib.Path) -> pathlib.Path:
    legacy = load_json(path)
    preset = copy.deepcopy(legacy["Template"])
    share_code = str(preset["ShareCode"]).upper()
    preset.pop("TemplateId", None)
    path_rules = preset.get("PathRules") or []

    if share_code == "872ED":
        preset["PathRules"] = []
        preset["DiscoverySources"] = [mine_rewind_source()]
        preset["RequiredPluginIds"] = [MINE_REWIND_ID]
        preset["IsRecommended"] = True
    elif share_code == "CS8LQ":
        preset["DiscoverySources"] = [mine_rewind_source(), inline_source(path_rules)]
        preset["RequiredPluginIds"] = [MINE_REWIND_ID]
        preset["IsRecommended"] = False
    else:
        preset["DiscoverySources"] = [inline_source(path_rules)]
        preset["IsRecommended"] = False

    envelope = {
        "Magic": "FolderRewindBackupPreset",
        "SchemaVersion": "2.0",
        "ExportedAtUtc": legacy.get("ExportedAtUtc"),
        "Preset": preset,
    }
    destination = PRESETS_DIR / f"{share_code}.frpreset.json"
    destination.write_text(
        json.dumps(envelope, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return destination


def main() -> int:
    destinations = [migrate(path) for path in sorted(TEMPLATES_DIR.glob("*.json"))]
    print(f"Migrated {len(destinations)} V1 template(s) to Backup Preset V2.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
