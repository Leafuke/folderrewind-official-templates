**简体中文** | [English](README_en.md)

# FolderRewind 官方模板库

这是 [FolderRewind](https://github.com/Leafuke/FolderRewind) 的官方模板仓库。

**FolderRewind** 是一款用于管理、备份和恢复目录状态的实用工具。为了方便用户快速应用常用的目录规则（如忽略特定缓存文件夹、备份特定数据目录），我们设立了此官方模板库。用户可以直接在 FolderRewind 客户端中浏览、下载和应用这些经过审核的、安全可靠的官方模板。

FolderRewind 支持将现有配置保存为模板供后续反复使用，并支持模板分享。模板不仅记录配置名称，还会保存一整套可复用的备份方案，例如备份策略、自动化触发器、过滤器设定、路径规则以及各类插件扩展属性等。你可以通过分享码或直接在这个官方库列表中轻松发现并导入别人的实用经验。关于如何在本地制作、修改模板，或是如何将其分享给社区的其他小伙伴，可以参阅[模板：创建与使用](https://folderrewind.top/docs/guides/templates)以及[模板：分享与导入](https://folderrewind.top/docs/guides/template-sharing)。

## 仓库结构

```
folderrewind-official-templates/
├── templates/                     # 已通过审核的模板文件，每个分享码对应一个文件
├── index.json                     # 供 FolderRewind 客户端读取的轻量级索引文件
├── schema.json                    # 模板仓库发布时的验证结构规范 (Schema)
├── scripts/
│   ├── validate_template.py       # PR 验证入口脚本，用于验证新提交的模板是否合规
│   └── rebuild_index.py           # 重建脚本，将 templates/ 目录下的文件打包到 index.json
└── .github/
    ├── workflows/
    │   ├── validate-template.yml
    │   └── rebuild-index.yml
    └── PULL_REQUEST_TEMPLATE.md
```

## 发布与合规规则

- 	emplates/ 目录中的每个文件必须命名为 {ShareCode}.json（例如 A1B2C.json）。
- **分享码 (ShareCode)** 必须由 5 个字符组成，字符范围为 A-HJ-NP-Z2-9（排除了容易混淆的字符）。
- 文件的顶层结构必须符合 FolderRewind 模板包的要求：
  - Magic = "FolderRewindTemplate" （魔术字符串标识）
  - SchemaVersion （架构版本）
  - Template （模板对象）
- Template.TemplateId 是追踪更新的唯一稳定标识符。
- Template.ShareCode 必须与文件名严格一致。
- 必须包含 Template.Name（名称）、Template.Description（描述），以及至少一条路径规则 (PathRule)。
- **安全检查**：包含危险路径（如绝对路径、.. 上级目录跳转，或系统核心目录）的提交将被直接拒绝。

## 客户端交互约定

FolderRewind 应用程序仅依赖此仓库的 index.json 文件即可完成以下操作：
- 浏览官方精选模板列表
- 解析和查找分享码 (Share Codes)
- 验证下载模板的哈希有效性

当用户在客户端选择一个模板时，应用程序将直接从 	emplates/{ShareCode}.json 下载匹配的文件，验证其 sha256 校验和，最后将其导入到本地的模板库中供使用。

## 审核与提交流程

如果您想向官方库贡献模板，请遵循以下流程：

1. 贡献者在 	emplates/ 目录下提交一个新的或修改现有的模板文件 (PR)。
2. GitHub Actions (validate-template.yml) 将自动执行以下检查：
   - 文件名及分享码格式是否合规
   - JSON 结构体是否符合规范
   - 必填字段是否遗漏
   - 是否存在重复的分享码
   - 是否包含危险的路径规则
3. 仓库维护者对 PR 进行人工 Review。
4. PR 合并到主分支后，
ebuild-index.yml 将自动运行并重新生成发布的 index.json 文件。

## 注意事项

- index.json 是通过脚本自动生成的。除非您清楚自己在做什么，否则**不要手动编辑此文件**。
- schema.json 只是本仓库发布流程的安全契约。为了保证安全，FolderRewind 客户端在下载模板后，在运行时依然会/应当独立验证其内容的安全性。
