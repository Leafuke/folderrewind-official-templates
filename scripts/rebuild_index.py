from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone


ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / "templates"
INDEX_PATH = ROOT / "index.json"


def sha256_hex(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def load_json(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_index_entry(path: pathlib.Path) -> dict:
    data = load_json(path)
    template = data["Template"]
    updated = template.get("UpdatedUtc") or data.get("ExportedAtUtc") or datetime.now(timezone.utc).isoformat()
    return {
        "shareCode": template.get("ShareCode", path.stem.upper()),
        "templateId": template.get("TemplateId") or template.get("ShareId") or "",
        "name": template.get("Name", ""),
        "author": template.get("Author", ""),
        "description": template.get("Description", ""),
        "gameName": template.get("GameName", ""),
        "steamAppId": template.get("SteamAppId"),
        "version": template.get("Version", "1.0"),
        "updatedUtc": updated,
        "baseConfigType": template.get("BaseConfigType", "Default"),
        "requiredPluginIds": template.get("RequiredPluginIds") or [],
        "fileUrl": f"templates/{path.name}",
        "sha256": sha256_hex(path),
        "isDisabled": False,
    }


def main() -> int:
    entries = [
        build_index_entry(path)
        for path in sorted(TEMPLATES_DIR.glob("*.json"))
    ]
    entries.sort(key=lambda item: ((item.get("gameName") or "").lower(), (item.get("name") or "").lower(), item.get("shareCode") or ""))
    document = {
        "schemaVersion": "1.0",
        "generatedAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "templates": entries,
    }
    INDEX_PATH.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Rebuilt {INDEX_PATH} with {len(entries)} template(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
