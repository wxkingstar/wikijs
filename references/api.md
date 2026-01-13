# Wiki.js GraphQL API 完整参考

## 概述

Wiki.js 使用 GraphQL API 进行所有数据操作。API 端点位于 `/graphql`。

## 认证

所有 API 请求需要在 Header 中包含 Bearer Token：

```
Authorization: Bearer YOUR_API_TOKEN
```

Token 通过 Wiki.js 管理后台 → API Access 生成。

## 数据库结构

### pages 表（核心）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 页面 ID（主键） |
| path | VARCHAR(255) | 页面路径（不含 locale） |
| hash | VARCHAR(255) | 路径哈希 |
| title | VARCHAR(255) | 页面标题 |
| description | VARCHAR(255) | 页面描述 |
| isPrivate | BOOLEAN | 是否私有 |
| isPublished | BOOLEAN | 是否发布 |
| content | TEXT | 页面源内容 |
| render | TEXT | 渲染后的 HTML |
| toc | JSON | 目录结构 |
| contentType | VARCHAR(255) | 内容类型（markdown/html 等） |
| editorKey | VARCHAR(255) | 编辑器类型 |
| localeCode | VARCHAR(5) | 语言代码 |
| authorId | INTEGER | 作者 ID |
| creatorId | INTEGER | 创建者 ID |
| createdAt | VARCHAR(255) | 创建时间 |
| updatedAt | VARCHAR(255) | 更新时间 |

### pageTree 表（目录树）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 节点 ID |
| path | VARCHAR(255) | 节点路径 |
| depth | INTEGER | 深度层级 |
| title | VARCHAR(255) | 节点标题 |
| isFolder | BOOLEAN | 是否为文件夹 |
| parent | INTEGER | 父节点 ID |
| pageId | INTEGER | 关联的页面 ID |
| localeCode | VARCHAR(5) | 语言代码 |
| ancestors | JSON | 祖先节点列表 |

### tags 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 标签 ID |
| tag | VARCHAR(255) | 标签名（唯一） |
| title | VARCHAR(255) | 标签显示名 |
| createdAt | VARCHAR(255) | 创建时间 |
| updatedAt | VARCHAR(255) | 更新时间 |

### editors 表

| key | 说明 |
|-----|------|
| markdown | Markdown 编辑器（推荐） |
| code | HTML 代码编辑器 |
| ckeditor | 富文本编辑器 |
| asciidoc | AsciiDoc 编辑器 |
| wysiwyg | 所见即所得编辑器 |
| redirect | 重定向页面 |

## Query 操作

### pages.list - 列出页面

```graphql
query {
  pages {
    list(
      limit: Int           # 返回数量限制
      orderBy: PageOrderBy # 排序方式: CREATED, ID, PATH, TITLE, UPDATED
      orderByDirection: PageOrderByDirection # 排序方向: ASC, DESC
      tags: [String]       # 按标签筛选
      locale: String       # 按语言筛选
      creatorId: Int       # 按创建者筛选
      authorId: Int        # 按作者筛选
    ) {
      id
      path
      locale
      title
      description
      contentType
      isPublished
      isPrivate
      privateNS
      publishStartDate
      publishEndDate
      tags
      createdAt
      updatedAt
    }
  }
}
```

### pages.single - 获取单个页面

```graphql
query {
  pages {
    single(id: Int!) {
      id
      path
      hash
      title
      description
      isPrivate
      isPublished
      privateNS
      publishStartDate
      publishEndDate
      content
      render
      toc
      contentType
      createdAt
      updatedAt
      editor
      locale
      scriptCss
      scriptJs
      authorId
      authorName
      authorEmail
      creatorId
      creatorName
      creatorEmail
      tags {
        id
        tag
        title
        createdAt
        updatedAt
      }
    }
  }
}
```

### pages.singleByPath - 通过路径获取页面

```graphql
query {
  pages {
    singleByPath(
      path: String!  # 页面路径
      locale: String! # 语言代码
    ) {
      # 返回字段同 single
    }
  }
}
```

### pages.search - 搜索页面

```graphql
query {
  pages {
    search(
      query: String!  # 搜索关键词
      path: String    # 路径前缀筛选
      locale: String  # 语言筛选
    ) {
      results {
        id
        title
        description
        path
        locale
      }
      suggestions
      totalHits
    }
  }
}
```

### pages.tree - 获取页面树

```graphql
query {
  pages {
    tree(
      path: String    # 根路径
      parent: Int     # 父节点 ID
      mode: PageTreeMode # ALL, FOLDERS, PAGES
      locale: String!
      includeAncestors: Boolean
    ) {
      id
      path
      depth
      title
      isPrivate
      isFolder
      privateNS
      parent
      pageId
      locale
    }
  }
}
```

### pages.tags - 获取所有标签

```graphql
query {
  pages {
    tags {
      id
      tag
      title
      createdAt
      updatedAt
    }
  }
}
```

### pages.history - 获取页面历史

```graphql
query {
  pages {
    history(
      id: Int!        # 页面 ID
      offsetPage: Int # 分页偏移
      offsetSize: Int # 分页大小
    ) {
      trail {
        versionId
        versionDate
        authorId
        authorName
        actionType
        valueBefore
        valueAfter
      }
      total
    }
  }
}
```

## Mutation 操作

### pages.create - 创建页面

```graphql
mutation {
  pages {
    create(
      content: String!      # 页面内容
      description: String!  # 页面描述
      editor: String!       # 编辑器类型 (markdown/code/etc)
      isPublished: Boolean! # 是否发布
      isPrivate: Boolean!   # 是否私有
      locale: String!       # 语言代码
      path: String!         # 页面路径
      publishEndDate: Date  # 发布结束日期
      publishStartDate: Date # 发布开始日期
      scriptCss: String     # 自定义 CSS
      scriptJs: String      # 自定义 JS
      tags: [String]!       # 标签列表
      title: String!        # 页面标题
    ) {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
      page {
        id
        path
        title
      }
    }
  }
}
```

### pages.update - 更新页面

```graphql
mutation {
  pages {
    update(
      id: Int!              # 页面 ID
      content: String       # 新内容
      description: String   # 新描述
      editor: String        # 编辑器类型
      isPublished: Boolean  # 是否发布
      isPrivate: Boolean    # 是否私有
      locale: String        # 语言代码
      path: String          # 新路径
      publishEndDate: Date
      publishStartDate: Date
      scriptCss: String
      scriptJs: String
      tags: [String]        # 新标签
      title: String         # 新标题
    ) {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
      page {
        id
        path
        title
        updatedAt
      }
    }
  }
}
```

### pages.delete - 删除页面

```graphql
mutation {
  pages {
    delete(id: Int!) {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
    }
  }
}
```

### pages.render - 重新渲染页面

```graphql
mutation {
  pages {
    render(id: Int!) {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
    }
  }
}
```

### pages.move - 移动页面

```graphql
mutation {
  pages {
    move(
      id: Int!              # 页面 ID
      destinationPath: String! # 目标路径
      destinationLocale: String! # 目标语言
    ) {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
    }
  }
}
```

### pages.rebuildTree - 重建页面树

```graphql
mutation {
  pages {
    rebuildTree {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
    }
  }
}
```

### pages.flushCache - 清除缓存

```graphql
mutation {
  pages {
    flushCache {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
    }
  }
}
```

### pages.migrateToLocale - 迁移语言

```graphql
mutation {
  pages {
    migrateToLocale(
      sourceLocale: String!
      targetLocale: String!
    ) {
      responseResult {
        succeeded
        errorCode
        slug
        message
      }
    }
  }
}
```

## ResponseResult 结构

所有 Mutation 操作返回统一的 ResponseResult：

```graphql
type ResponseResult {
  succeeded: Boolean!   # 是否成功
  errorCode: Int!       # 错误代码 (0 = 成功)
  slug: String!         # 错误标识符
  message: String       # 错误消息
}
```

## 常见错误代码

| errorCode | slug | 说明 |
|-----------|------|------|
| 0 | - | 成功 |
| 1 | ERR_GENERIC | 通用错误 |
| 2 | ERR_DUPLICATE_KEY | 路径已存在 |
| 3 | ERR_PAGE_NOT_FOUND | 页面不存在 |
| 4 | ERR_PAGE_MOVE_FAILED | 移动页面失败 |
| 5 | ERR_PAGE_UPDATE_FAILED | 更新页面失败 |
| 6 | ERR_UNAUTHORIZED | 未授权 |
| 7 | ERR_FORBIDDEN | 禁止访问 |

## 用户相关 API

### users.list - 列出用户

```graphql
query {
  users {
    list(
      filter: String
      orderBy: String
    ) {
      id
      name
      email
      providerKey
      isSystem
      isActive
      createdAt
      lastLoginAt
    }
  }
}
```

### users.single - 获取用户

```graphql
query {
  users {
    single(id: Int!) {
      id
      name
      email
      providerKey
      providerId
      isSystem
      isActive
      isVerified
      location
      jobTitle
      timezone
      dateFormat
      appearance
      createdAt
      updatedAt
      lastLoginAt
      groups {
        id
        name
      }
    }
  }
}
```

## 分组相关 API

### groups.list - 列出分组

```graphql
query {
  groups {
    list(
      filter: String
      orderBy: String
    ) {
      id
      name
      isSystem
      userCount
      createdAt
      updatedAt
    }
  }
}
```

## cURL 示例

### 列出所有页面
```bash
curl -X POST http://localhost:3000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "{ pages { list { id path title } } }"}'
```

### 创建 Markdown 页面
```bash
curl -X POST http://localhost:3000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "mutation($content: String!, $path: String!, $title: String!) { pages { create(content: $content, description: \"\", editor: \"markdown\", isPublished: true, isPrivate: false, locale: \"zh\", path: $path, tags: [], title: $title) { responseResult { succeeded message } page { id } } } }",
    "variables": {
      "content": "# Hello World\n\nThis is a test page.",
      "path": "test/hello-world",
      "title": "Hello World"
    }
  }'
```

### 搜索页面
```bash
curl -X POST http://localhost:3000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "{ pages { search(query: \"keyword\") { results { id title path } totalHits } } }"}'
```

## 直接数据库操作

当 API 不可用时，可通过 PostgreSQL 直接操作：

```sql
-- 查询页面
SELECT id, path, title, "updatedAt" FROM pages WHERE path LIKE 'projects/%';

-- 获取页面内容
SELECT content FROM pages WHERE id = 123;

-- 插入页面（不推荐，需手动处理很多字段）
-- 建议始终使用 GraphQL API
```

**注意**：直接操作数据库后，可能需要重建页面树和清除缓存：
```graphql
mutation { pages { rebuildTree { responseResult { succeeded } } } }
mutation { pages { flushCache { responseResult { succeeded } } } }
```
