## Preset metadata

- Share code:
- Share ID:
- Preset name:
- Game/application:
- Author:
- Version:

## Description

Describe the data covered, the intended DiscoverySources, and any plugin requirements.

## Checklist

- [ ] The file is `presets/{ShareCode}.frpreset.json`
- [ ] `Preset.ShareCode` matches the file name
- [ ] `Preset.ShareId` is stable for updates to an existing Preset
- [ ] The Preset has at least one valid InlinePathRules or ProviderReference source
- [ ] Every ProviderReference contains a stable ProviderId and DefinitionId
- [ ] ExternalIds are real and verifiable; none were invented to force matching
- [ ] Inline rules contain no absolute paths, parent traversal, or dangerous system roots
- [ ] Required plugins are listed in RequiredPluginIds
- [ ] Both validation scripts pass
- [ ] Both indexes were rebuilt and contain no unexpected changes
