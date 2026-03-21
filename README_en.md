[简体中文](README.md) | English

# FolderRewind Official Templates

This is the official curated template repository for [FolderRewind](https://github.com/Leafuke/FolderRewind).

**FolderRewind** is a utility for managing, backing up, and restoring the states of directories. To help users quickly apply common directory rules (e.g., ignoring specific cache folders, backing up specific data directories), we set up this official template repository. Users can browse, download, and apply these reviewed, safe, and reliable official templates directly within the FolderRewind client.

FolderRewind supports saving existing configurations as templates for repeated use, and completing the template sharing loop. Templates save a reusable backup scheme, including backup strategies, automation presets, filters, path rules, and more. Users can create configurations from templates via share codes or by browsing the official list. For more details, see the [Templates Creation & Usage Guide](https://folderrewind.top/docs/guides/templates) and [Template Sharing & Import Guide](https://folderrewind.top/docs/guides/template-sharing).

## Repository Layout

`	ext
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
`

## Publishing Rules

- Each file in 	emplates/ must be named {ShareCode}.json (e.g., A1B2C.json).
- **ShareCode** must be 5 characters from A-HJ-NP-Z2-9 (excluding confusing characters).
- The file body must be a FolderRewind template envelope with:
  - Magic = "FolderRewindTemplate"
  - SchemaVersion
  - Template
- Template.TemplateId is the stable identity for update tracking.
- Template.ShareCode must match the file name.
- Template.Name, Template.Description, and at least one PathRule are required.
- **Security Check**: Dangerous path values such as absolute paths, .., or system directories are rejected.

## Client Contract

The app only needs index.json from this repository to:

- browse official templates
- resolve share codes
- validate downloaded template hashes

When a user selects a template, the app downloads the matching file from 	emplates/{ShareCode}.json, verifies sha256, then imports it into the local template library.

## Review Workflow

If you want to contribute a template to the official repository, please follow this workflow:

1. Contributor submits or updates a template file in 	emplates/ (PR).
2. GitHub Actions (alidate-template.yml) automatically checks:
   - filename/share code rules
   - envelope structure
   - required fields
   - duplicate share codes
   - dangerous path content
3. Maintainer reviews the PR manually.
4. After merge, 
ebuild-index.yml runs automatically and regenerates the published index.json.

## Notes

- index.json is generated. Unless you know what you are doing, **do not hand-edit this file**.
- schema.json is a publishing contract for this repository. FolderRewind clients should still validate downloaded content at runtime for security.
