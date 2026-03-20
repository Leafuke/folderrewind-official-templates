from __future__ import annotations

import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / "templates"
INDEX_PATH = ROOT / "index.json"
SHARE_CODE_RE = re.compile(r"^[A-HJ-NP-Z2-9]{5}$")
SYSTEM_SEGMENTS = {"windows", "system32", "program files", "program files (x86)", "users"}


def load_json(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_template_paths(argv: list[str]) -> list[pathlib.Path]:
    paths = []
    for arg in argv:
        path = pathlib.Path(arg).resolve()
        if path.is_file() and path.suffix.lower() == ".json" and path.parent == TEMPLATES_DIR:
            paths.append(path)
    if paths:
        return sorted(paths)
    return sorted(TEMPLATES_DIR.glob("*.json"))


def validate_path_rule(rule: dict, errors: list[str]) -> None:
    name = rule.get("Name") or "Unnamed rule"
    segments = rule.get("Segments") or []
    if not segments:
        errors.append(f"{name}: missing path segments")
        return
    for seg in segments:
        value = (seg or {}).get("Value", "")
        if not isinstance(value, str) or not value:
            continue
        lower = value.lower().strip()
        if ".." in value or ":" in value or "\\" in value or "/" in value:
            errors.append(f"{name}: unsafe segment value {value!r}")
            break
        if lower in SYSTEM_SEGMENTS:
            errors.append(f"{name}: sensitive segment value {value!r}")
            break
    for marker in rule.get("Markers") or []:
        value = (marker or {}).get("Value", "")
        if not isinstance(value, str) or not value:
            continue
        if ".." in value or "\\" in value or "/" in value or ":" in value:
            errors.append(f"{name}: unsafe marker value {value!r}")
            break


def validate_template_file(path: pathlib.Path, all_codes: set[str], template_ids: set[str]) -> list[str]:
    errors: list[str] = []
    file_share_code = path.stem.upper()
    if not SHARE_CODE_RE.fullmatch(file_share_code):
        errors.append(f"{path.name}: invalid filename share code")

    data = load_json(path)
    if data.get("Magic") != "FolderRewindTemplate":
        errors.append(f"{path.name}: Magic must be FolderRewindTemplate")

    template = data.get("Template")
    if not isinstance(template, dict):
        errors.append(f"{path.name}: missing Template object")
        return errors

    share_code = str(template.get("ShareCode") or "").upper()
    if share_code != file_share_code:
        errors.append(f"{path.name}: Template.ShareCode does not match filename")
    if not SHARE_CODE_RE.fullmatch(share_code):
        errors.append(f"{path.name}: invalid Template.ShareCode")

    template_id = str(template.get("TemplateId") or template.get("ShareId") or "").strip()
    if not template_id:
        errors.append(f"{path.name}: missing TemplateId")
    elif template_id in template_ids:
        errors.append(f"{path.name}: duplicate TemplateId {template_id}")
    else:
        template_ids.add(template_id)

    if share_code in all_codes:
        errors.append(f"{path.name}: duplicate ShareCode {share_code}")
    else:
        all_codes.add(share_code)

    if not str(template.get("Name") or "").strip():
        errors.append(f"{path.name}: missing template name")
    if not str(template.get("Description") or "").strip():
        errors.append(f"{path.name}: missing template description")

    rules = template.get("PathRules") or []
    if not isinstance(rules, list) or not rules:
        errors.append(f"{path.name}: missing path rules")
    else:
        for rule in rules:
            if isinstance(rule, dict):
                validate_path_rule(rule, errors)

    return errors


def validate_index() -> list[str]:
    errors: list[str] = []
    if not INDEX_PATH.exists():
        errors.append("index.json is missing")
        return errors
    data = load_json(INDEX_PATH)
    if not isinstance(data.get("templates", []), list):
        errors.append("index.json: templates must be an array")
    return errors


def main() -> int:
    template_paths = iter_template_paths(sys.argv[1:])
    errors = validate_index()
    all_codes: set[str] = set()
    template_ids: set[str] = set()
    for path in template_paths:
        errors.extend(validate_template_file(path, all_codes, template_ids))

    if errors:
        print("Template validation failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print("Template validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
