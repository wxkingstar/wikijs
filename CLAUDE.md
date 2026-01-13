# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 Claude Code Skill，用于通过 GraphQL API 管理 Wiki.js 文档中心。作为 `/wikijs` 技能被调用，支持公司 AI 应用文档的创建、读取、搜索和同步。

## 核心架构

```
wikijs/
├── SKILL.md              # 技能定义和 GraphQL API 使用指南
├── scripts/
│   └── wikijs_api.py     # Python CLI 客户端（WikiJSClient 类）
├── references/
│   └── api.md            # GraphQL API 完整参考
└── .env                  # 环境配置（WIKIJS_URL, WIKIJS_TOKEN）
```

## 常用命令

```bash
# 列出页面
python scripts/wikijs_api.py list --project wuji-stat

# 获取页面内容
python scripts/wikijs_api.py get --id 123

# 搜索文档
python scripts/wikijs_api.py search --query "关键词"

# 创建文档
python scripts/wikijs_api.py create --project my-project --path getting-started --title "快速开始" --file content.md

# 更新文档
python scripts/wikijs_api.py update --id 123 --file new_content.md

# 同步本地文件到 Wiki
python scripts/wikijs_api.py sync-file --project my-project --source README.md --target index

# 删除文档
python scripts/wikijs_api.py delete --id 123 --force
```

## API 调用模式

使用 curl 直接调用 GraphQL API：

```bash
curl -X POST http://localhost:3000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $WIKIJS_TOKEN" \
  -d '{"query": "{ pages { list { id path title } } }"}'
```

## 文档路径规范

- 项目文档位于 `/projects/{project-name}/` 路径下
- 每个目录需要 `index` 页面作为入口
- 路径使用小写字母和连字符：`my-project-name`

## 关键技术细节

- 创建页面必须设置 `editor: "markdown"`，否则内容显示为纯文本
- 页面更新后可能需要调用 `render` mutation 刷新缓存
- 依赖：`requests`, `python-dotenv`
