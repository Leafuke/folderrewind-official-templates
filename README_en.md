[简体中文](README.md) | **English**

# FolderRewind Official Backup Presets

This is the official curated Backup Preset repository for [FolderRewind](https://github.com/Leafuke/FolderRewind). New clients discover, verify, and import reviewed backup policies from this repository. Template V1 remains available as a read-only compatibility track.

## Repository layout

```text
folderrewind-official-templates/
├── presets/                       # Backup Preset V2 files, index, and schema
│   ├── {ShareCode}.frpreset.json
│   ├── index.json
│   └── schema.json
├── templates/                     # Read-only Template V1 compatibility files
├── index.json                     # V1 compatibility index
├── schema.json                    # V1 compatibility schema
├── scripts/
│   ├── validate_presets.py
│   ├── rebuild_preset_index.py
│   ├── validate_template.py
│   └── rebuild_index.py
└── .github/
```

New contributions must use `presets/{ShareCode}.frpreset.json` and are published through the generated `presets/index.json`. Do not add new V1 files under `templates/`, and do not hand-edit either generated index.

## Backup Preset V2 contract

V2 separates two concerns:

- `DiscoverySources` describe where data is located.
- Archive, Automation, Filters, BackupScope, Cloud, and related fields describe how it is backed up.

### Identities

`ProviderReference.ProviderId` is the stable identity of a Discovery Provider.

`ProviderReference.DefinitionId` is a stable game definition declared by that Provider.

For example:

```text
ProviderId   = com.folderrewind.minerewind
DefinitionId = minecraft-java
```

These identities are not interchangeable:

- `CandidateId` identifies a concrete discovery candidate; it is not a DefinitionId.
- `ConfigKindId` identifies configuration execution semantics; it is not a DefinitionId.
- `PluginId` identifies a plugin package and may differ from ProviderId.
- MineRewind currently uses the same PluginId and ProviderId, but that is not a general requirement.

Do not invent Steam IDs or other ExternalIds to force matching. ExternalIds must be real, verifiable, and stable.

### FolderRewind 1.9.x application semantics

| DiscoverySources | Manual application behavior |
| --- | --- |
| InlinePathRules only | Resolve paths directly and ask the user to confirm them |
| ProviderReference only | Run targeted Discovery, then review and commit |
| ProviderReference + InlinePathRules | Manual application uses inline rules; Game Discovery uses ProviderReference to associate discovered resources |

A ProviderReference-only Preset must not create a configuration directly from empty PathRules, and should not add unreliable fallback PathRules.

872ED is a valid provider-only example:

```text
ProviderId    = com.folderrewind.minerewind
DefinitionId  = minecraft-java
PathRules     = []
IsRecommended = true
```

## V2 publishing rules

- Files must be named `{ShareCode}.frpreset.json`.
- ShareCode is five characters from `A-HJ-NP-Z2-9`.
- `Preset.ShareCode` must match the file name.
- `ShareId` is the stable update identity across versions.
- A Preset requires a name, description, and at least one valid DiscoverySource.
- InlinePathRules must not contain absolute paths, parent traversal, or dangerous system roots.
- ProviderReference requires both ProviderId and DefinitionId.
- RequiredPluginIds list plugins required by the policy, but do not replace ProviderReference.

## Review and generation

Run before submitting:

```powershell
python scripts/validate_template.py
python scripts/validate_presets.py
python scripts/rebuild_index.py
python scripts/rebuild_preset_index.py
```

Confirm that generated files contain only expected changes. Pull requests validate both V1 and V2; after merge to `main`, the publishing workflow rebuilds the indexes.

Clients must still independently validate schema, hashes, path safety, Provider availability, and non-empty resolved sources. Repository review does not replace runtime defenses.
