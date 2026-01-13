# Wiki.js 文档中心管理助手

Claude Code Skill，通过 GraphQL API 管理公司 AI 应用文档中心。

## 功能

- 📄 创建/更新/删除 Wiki.js 页面
- 🔍 搜索和读取文档内容
- 🔄 同步代码库文档（README、CHANGELOG 等）到 Wiki.js
- 🏷️ 管理文档标签

## 安装

1. 确保 skill 目录位于 `~/.claude/skills/wikijs/`

2. 安装依赖：
```bash
pip install requests python-dotenv
```

3. 配置环境变量：
```bash
cp .env.example .env
```

4. 编辑 `.env` 文件，填入 Wiki.js 配置：
```
WIKIJS_URL=http://localhost:3000
WIKIJS_TOKEN=your_api_token_here
```

> Token 获取方式：Wiki.js 管理后台 → API Access → New API Key

## 使用方式

### 作为 Claude Code Skill

在 Claude Code 中使用 `/wikijs` 命令触发此技能，或在对话中提及相关关键词：
- wiki、文档中心、项目文档、wikijs、文档同步

### 命令行工具

```bash
# 列出项目文档
python scripts/wikijs_api.py list --project wuji-stat

# 获取页面内容
python scripts/wikijs_api.py get --id 123

# 通过路径获取页面
python scripts/wikijs_api.py get-by-path --path projects/wuji-stat/index

# 搜索文档
python scripts/wikijs_api.py search --query "API"

# 创建文档
python scripts/wikijs_api.py create \
  --project wuji-stat \
  --path getting-started \
  --title "快速开始" \
  --file content.md

# 更新文档
python scripts/wikijs_api.py update --id 123 --file new_content.md

# 同步本地文件到 Wiki
python scripts/wikijs_api.py sync-file \
  --project wuji-stat \
  --source README.md \
  --target index

# 删除文档
python scripts/wikijs_api.py delete --id 123

# 列出所有标签
python scripts/wikijs_api.py tags
```

## 文档结构规范

项目文档统一存放在 `/projects/{project-name}/` 路径下：

```
/projects/{project-name}/
├── index                 # 项目首页（必须）
├── getting-started       # 快速开始
├── architecture          # 架构说明
├── api/
│   ├── index             # API 概览
│   └── {endpoint}        # 各端点文档
├── guides/
│   └── {guide-name}      # 使用指南
└── changelog             # 更新日志
```

## 参考文档

- [SKILL.md](SKILL.md) - 技能定义和 GraphQL API 快速参考
- [references/api.md](references/api.md) - GraphQL API 完整参考
- [Wiki.js 官方文档](https://docs.requarks.io/)
