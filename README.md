# FolderRewind Official Templates

Official reviewed templates for FolderRewind.

## Repository Layout

```text
folderrewind-official-templates/
├── templates/                     # Reviewed template files, one file per share code
├── index.json                     # Lightweight client index consumed by FolderRewind
├── schema.json                    # Publishing schema for template repository files
├── scripts/
│   ├── validate_template.py       # PR validation entrypoint
│   └── rebuild_index.py           # Rebuilds index.json from templates/
└── .github/
    ├── workflows/
    │   ├── validate-template.yml
    │   └── rebuild-index.yml
    └── PULL_REQUEST_TEMPLATE.md
```

## Publishing Rules

- Each file in `templates/` must be named `{ShareCode}.json`.
- `ShareCode` must be 5 characters from `A-HJ-NP-Z2-9`.
- The file body must be a FolderRewind template envelope with:
  - `Magic = "FolderRewindTemplate"`
  - `SchemaVersion`
  - `Template`
- `Template.TemplateId` is the stable identity for update tracking.
- `Template.ShareCode` must match the file name.
- `Template.Name`, `Template.Description`, and at least one `PathRule` are required.
- Dangerous path values such as absolute paths, `..`, or system directories are rejected.

## Client Contract

The app only needs `index.json` to:

- browse official templates
- resolve share codes
- validate downloaded template hashes

When a user selects a template, the app downloads the matching file from `templates/{ShareCode}.json`, verifies `sha256`, then imports it into the local template library.

## Review Workflow

1. Contributor submits or updates a template file in `templates/`.
2. `validate-template.yml` checks:
   - filename/share code rules
   - envelope structure
   - required fields
   - duplicate share codes
   - dangerous path content
3. Maintainer reviews the PR.
4. After merge, `rebuild-index.yml` regenerates `index.json`.

## Notes

- `index.json` is generated. Do not hand-edit it unless you know what you are doing.
- `schema.json` is a publishing contract for this repository. FolderRewind clients should still validate downloaded content at runtime.
