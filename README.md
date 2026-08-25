**简体中文** | [English](README_en.md)

# FolderRewind 官方备份方案库

这是 [FolderRewind](https://github.com/Leafuke/FolderRewind) 的官方 Backup Preset 仓库。新客户端通过本仓库发现、校验并导入经过审核的备份策略；旧版 Template V1 继续作为只读兼容轨提供。

## 仓库结构

```text
folderrewind-official-templates/
├── presets/                       # Backup Preset V2 文件、索引和 schema
│   ├── {ShareCode}.frpreset.json
│   ├── index.json
│   └── schema.json
├── templates/                     # 只读 Template V1 兼容文件
├── index.json                     # V1 兼容索引
├── schema.json                    # V1 兼容 schema
├── scripts/
│   ├── validate_presets.py
│   ├── rebuild_preset_index.py
│   ├── validate_template.py
│   └── rebuild_index.py
└── .github/
```

新贡献必须使用 `presets/{ShareCode}.frpreset.json`，并通过生成的 `presets/index.json` 发布。不要向 `templates/` 添加新的 V1 文件，也不要手工编辑两个生成索引。

## Backup Preset V2 契约

V2 把两类信息分开：

- `DiscoverySources` 描述“数据在哪里”。
- Archive、Automation、Filters、BackupScope、Cloud 等字段描述“如何备份”。

### 身份定义

`ProviderReference.ProviderId` 是稳定的 Discovery Provider 身份。

`ProviderReference.DefinitionId` 是该 Provider 自己声明的稳定游戏定义身份。

例如：

```text
ProviderId   = com.folderrewind.minerewind
DefinitionId = minecraft-java
```

以下身份不能混用：

- `CandidateId` 标识某个实际发现候选，不等于 DefinitionId。
- `ConfigKindId` 标识配置执行语义，不等于 DefinitionId。
- `PluginId` 标识插件包；它可以与 ProviderId 不同。
- MineRewind 当前的 PluginId 与 ProviderId 恰好相同，这不是通用约束。

不要为匹配而杜撰 Steam ID 或其他 ExternalIds。ExternalIds 只能填写可验证、长期稳定的真实标识。

### 1.9.x 应用语义

| DiscoverySources | 手工应用行为 |
| --- | --- |
| 只有 InlinePathRules | 客户端直接解析路径并让用户确认 |
| 只有 ProviderReference | 客户端执行定向 Discovery，再 review/commit |
| ProviderReference + InlinePathRules | 手工应用使用 inline rules；Game Discovery 使用 ProviderReference 关联已发现资源 |

ProviderReference-only Preset 不得通过空 PathRules 直接创建配置，也不应添加不可靠的 fallback PathRules。

872ED 是合法的 provider-only 代表：

```text
ProviderId    = com.folderrewind.minerewind
DefinitionId  = minecraft-java
PathRules     = []
IsRecommended = true
```

## V2 发布规则

- 文件名必须为 `{ShareCode}.frpreset.json`。
- ShareCode 为 5 位 `A-HJ-NP-Z2-9` 字符。
- `Preset.ShareCode` 必须与文件名一致。
- `ShareId` 是跨版本跟踪更新的稳定身份。
- Preset 必须包含名称、描述和至少一个有效 DiscoverySource。
- InlinePathRules 不得包含绝对路径、上级目录跳转或危险系统根目录。
- ProviderReference 必须同时包含 ProviderId 与 DefinitionId。
- RequiredPluginIds 应列出应用策略所必需的插件，但不能代替 ProviderReference。

## 审核与生成

提交前运行：

```powershell
python scripts/validate_template.py
python scripts/validate_presets.py
python scripts/rebuild_index.py
python scripts/rebuild_preset_index.py
```

确认生成结果只有预期差异后再提交。PR 会再次运行 V1/V2 校验；合并到 `main` 后，工作流会重建发布索引。

客户端仍必须对下载内容做独立的 schema、哈希、路径安全、Provider 可用性和最终非空来源检查；仓库审核不能替代运行时防线。
