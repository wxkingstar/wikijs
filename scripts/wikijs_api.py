#!/usr/bin/env python3
"""
Wiki.js GraphQL API 操作脚本
用于管理公司 AI 应用文档中心
"""

import argparse
import json
import os
import sys
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

WIKIJS_URL = os.getenv('WIKIJS_URL', 'http://localhost:3000')
WIKIJS_TOKEN = os.getenv('WIKIJS_TOKEN', '')
GRAPHQL_ENDPOINT = f"{WIKIJS_URL}/graphql"


class WikiJSClient:
    """Wiki.js GraphQL API 客户端"""

    def __init__(self, url: str = WIKIJS_URL, token: str = WIKIJS_TOKEN):
        self.url = url
        self.token = token
        self.endpoint = f"{url}/graphql"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

    def _execute(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """执行 GraphQL 查询"""
        payload = {'query': query}
        if variables:
            payload['variables'] = variables

        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if 'errors' in result:
                raise Exception(f"GraphQL Error: {result['errors']}")

            return result.get('data', {})
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def list_pages(self, project: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """列出页面"""
        query = """
        query ($limit: Int) {
            pages {
                list(limit: $limit, orderBy: PATH) {
                    id
                    path
                    title
                    description
                    updatedAt
                    createdAt
                }
            }
        }
        """
        result = self._execute(query, {'limit': limit})
        pages = result.get('pages', {}).get('list', [])

        if project:
            prefix = f"projects/{project}/"
            pages = [p for p in pages if p['path'].startswith(prefix) or p['path'] == f"projects/{project}"]

        return pages

    def get_page(self, page_id: int) -> Optional[Dict]:
        """获取页面详情"""
        query = """
        query ($id: Int!) {
            pages {
                single(id: $id) {
                    id
                    path
                    title
                    description
                    content
                    contentType
                    createdAt
                    updatedAt
                    tags {
                        tag
                        title
                    }
                }
            }
        }
        """
        result = self._execute(query, {'id': page_id})
        return result.get('pages', {}).get('single')

    def get_page_by_path(self, path: str, locale: str = 'zh') -> Optional[Dict]:
        """通过路径获取页面"""
        query = """
        query ($path: String!, $locale: String!) {
            pages {
                singleByPath(path: $path, locale: $locale) {
                    id
                    path
                    title
                    description
                    content
                    contentType
                    createdAt
                    updatedAt
                }
            }
        }
        """
        result = self._execute(query, {'path': path, 'locale': locale})
        return result.get('pages', {}).get('singleByPath')

    def search_pages(self, query_text: str, limit: int = 20) -> Dict:
        """搜索页面"""
        query = """
        query ($query: String!) {
            pages {
                search(query: $query) {
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
        """
        result = self._execute(query, {'query': query_text})
        return result.get('pages', {}).get('search', {})

    def create_page(
        self,
        path: str,
        title: str,
        content: str,
        description: str = '',
        editor: str = 'markdown',
        locale: str = 'zh',
        tags: List[str] = None,
        is_published: bool = True,
        is_private: bool = False
    ) -> Dict:
        """创建页面"""
        query = """
        mutation (
            $path: String!
            $title: String!
            $content: String!
            $description: String!
            $editor: String!
            $locale: String!
            $tags: [String]!
            $isPublished: Boolean!
            $isPrivate: Boolean!
        ) {
            pages {
                create(
                    path: $path
                    title: $title
                    content: $content
                    description: $description
                    editor: $editor
                    locale: $locale
                    tags: $tags
                    isPublished: $isPublished
                    isPrivate: $isPrivate
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
        """
        variables = {
            'path': path,
            'title': title,
            'content': content,
            'description': description,
            'editor': editor,
            'locale': locale,
            'tags': tags or [],
            'isPublished': is_published,
            'isPrivate': is_private
        }
        result = self._execute(query, variables)
        return result.get('pages', {}).get('create', {})

    def update_page(
        self,
        page_id: int,
        content: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """更新页面"""
        # 先获取现有页面信息
        existing = self.get_page(page_id)
        if not existing:
            raise Exception(f"Page {page_id} not found")

        query = """
        mutation (
            $id: Int!
            $content: String!
            $title: String!
            $description: String!
            $tags: [String]!
        ) {
            pages {
                update(
                    id: $id
                    content: $content
                    title: $title
                    description: $description
                    tags: $tags
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
        """
        variables = {
            'id': page_id,
            'content': content if content is not None else existing['content'],
            'title': title if title is not None else existing['title'],
            'description': description if description is not None else (existing.get('description') or ''),
            'tags': tags if tags is not None else [t['tag'] for t in existing.get('tags', [])]
        }
        result = self._execute(query, variables)
        return result.get('pages', {}).get('update', {})

    def delete_page(self, page_id: int) -> Dict:
        """删除页面"""
        query = """
        mutation ($id: Int!) {
            pages {
                delete(id: $id) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                }
            }
        }
        """
        result = self._execute(query, {'id': page_id})
        return result.get('pages', {}).get('delete', {})

    def render_page(self, page_id: int) -> Dict:
        """重新渲染页面"""
        query = """
        mutation ($id: Int!) {
            pages {
                render(id: $id) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                }
            }
        }
        """
        result = self._execute(query, {'id': page_id})
        return result.get('pages', {}).get('render', {})

    def list_tags(self) -> List[Dict]:
        """列出所有标签"""
        query = """
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
        """
        result = self._execute(query)
        return result.get('pages', {}).get('tags', [])


def format_page_list(pages: List[Dict]) -> str:
    """格式化页面列表输出"""
    if not pages:
        return "No pages found."

    output = []
    output.append(f"{'ID':<6} {'Path':<50} {'Title':<30}")
    output.append("-" * 90)
    for page in pages:
        output.append(f"{page['id']:<6} {page['path']:<50} {page['title']:<30}")
    return "\n".join(output)


def format_page_detail(page: Dict) -> str:
    """格式化页面详情输出"""
    if not page:
        return "Page not found."

    output = []
    output.append(f"ID: {page['id']}")
    output.append(f"Path: {page['path']}")
    output.append(f"Title: {page['title']}")
    output.append(f"Description: {page.get('description', '')}")
    output.append(f"Content Type: {page.get('contentType', '')}")
    output.append(f"Created: {page.get('createdAt', '')}")
    output.append(f"Updated: {page.get('updatedAt', '')}")
    if page.get('tags'):
        output.append(f"Tags: {', '.join(t['tag'] for t in page['tags'])}")
    output.append("\n--- Content ---\n")
    output.append(page.get('content', ''))
    return "\n".join(output)


def sync_file_to_wiki(
    client: WikiJSClient,
    project: str,
    source_file: str,
    target_path: str,
    title: Optional[str] = None
) -> Dict:
    """同步文件到 Wiki.js"""
    source = Path(source_file)
    if not source.exists():
        raise Exception(f"Source file not found: {source_file}")

    content = source.read_text(encoding='utf-8')
    full_path = f"projects/{project}/{target_path}"

    # 尝试获取现有页面
    existing = client.get_page_by_path(full_path)

    if not title:
        # 从内容提取标题
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        if not title:
            title = target_path.replace('-', ' ').title()

    if existing:
        # 更新现有页面
        result = client.update_page(
            page_id=existing['id'],
            content=content,
            title=title
        )
        action = "Updated"
    else:
        # 创建新页面
        result = client.create_page(
            path=full_path,
            title=title,
            content=content,
            tags=[f"project:{project}"]
        )
        action = "Created"

    return {'action': action, 'result': result}


def main():
    parser = argparse.ArgumentParser(description='Wiki.js API CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # list 命令
    list_parser = subparsers.add_parser('list', help='List pages')
    list_parser.add_argument('--project', '-p', help='Filter by project name')
    list_parser.add_argument('--limit', '-l', type=int, default=100, help='Max results')

    # get 命令
    get_parser = subparsers.add_parser('get', help='Get page by ID')
    get_parser.add_argument('--id', '-i', type=int, required=True, help='Page ID')

    # get-by-path 命令
    get_path_parser = subparsers.add_parser('get-by-path', help='Get page by path')
    get_path_parser.add_argument('--path', '-p', required=True, help='Page path')
    get_path_parser.add_argument('--locale', '-l', default='zh', help='Locale')

    # search 命令
    search_parser = subparsers.add_parser('search', help='Search pages')
    search_parser.add_argument('--query', '-q', required=True, help='Search query')

    # create 命令
    create_parser = subparsers.add_parser('create', help='Create page')
    create_parser.add_argument('--project', '-p', required=True, help='Project name')
    create_parser.add_argument('--path', required=True, help='Page path (relative to project)')
    create_parser.add_argument('--title', '-t', required=True, help='Page title')
    create_parser.add_argument('--content', '-c', help='Page content (or use --file)')
    create_parser.add_argument('--file', '-f', help='Read content from file')
    create_parser.add_argument('--description', '-d', default='', help='Page description')
    create_parser.add_argument('--tags', nargs='*', default=[], help='Tags')

    # update 命令
    update_parser = subparsers.add_parser('update', help='Update page')
    update_parser.add_argument('--id', '-i', type=int, required=True, help='Page ID')
    update_parser.add_argument('--content', '-c', help='New content (or use --file)')
    update_parser.add_argument('--file', '-f', help='Read content from file')
    update_parser.add_argument('--title', '-t', help='New title')
    update_parser.add_argument('--description', '-d', help='New description')

    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='Delete page')
    delete_parser.add_argument('--id', '-i', type=int, required=True, help='Page ID')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')

    # render 命令
    render_parser = subparsers.add_parser('render', help='Re-render page')
    render_parser.add_argument('--id', '-i', type=int, required=True, help='Page ID')

    # sync-file 命令
    sync_parser = subparsers.add_parser('sync-file', help='Sync file to Wiki.js')
    sync_parser.add_argument('--project', '-p', required=True, help='Project name')
    sync_parser.add_argument('--source', '-s', required=True, help='Source file path')
    sync_parser.add_argument('--target', '-t', required=True, help='Target page path')
    sync_parser.add_argument('--title', help='Page title')

    # tags 命令
    subparsers.add_parser('tags', help='List all tags')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not WIKIJS_TOKEN:
        print("Error: WIKIJS_TOKEN not set. Please configure ~/.claude/skills/wikijs/.env")
        sys.exit(1)

    client = WikiJSClient()

    try:
        if args.command == 'list':
            pages = client.list_pages(project=args.project, limit=args.limit)
            print(format_page_list(pages))

        elif args.command == 'get':
            page = client.get_page(args.id)
            print(format_page_detail(page))

        elif args.command == 'get-by-path':
            page = client.get_page_by_path(args.path, args.locale)
            print(format_page_detail(page))

        elif args.command == 'search':
            result = client.search_pages(args.query)
            print(f"Found {result.get('totalHits', 0)} results:\n")
            for r in result.get('results', []):
                print(f"  [{r['id']}] {r['path']}: {r['title']}")

        elif args.command == 'create':
            content = args.content
            if args.file:
                content = Path(args.file).read_text(encoding='utf-8')
            if not content:
                print("Error: --content or --file required")
                sys.exit(1)

            full_path = f"projects/{args.project}/{args.path}"
            tags = list(args.tags) + [f"project:{args.project}"]

            result = client.create_page(
                path=full_path,
                title=args.title,
                content=content,
                description=args.description,
                tags=tags
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'update':
            content = args.content
            if args.file:
                content = Path(args.file).read_text(encoding='utf-8')

            result = client.update_page(
                page_id=args.id,
                content=content,
                title=args.title,
                description=args.description
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'delete':
            if not args.force:
                page = client.get_page(args.id)
                if page:
                    confirm = input(f"Delete page '{page['title']}' ({page['path']})? [y/N] ")
                    if confirm.lower() != 'y':
                        print("Cancelled.")
                        sys.exit(0)

            result = client.delete_page(args.id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'render':
            result = client.render_page(args.id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == 'sync-file':
            result = sync_file_to_wiki(
                client,
                project=args.project,
                source_file=args.source,
                target_path=args.target,
                title=args.title
            )
            print(f"{result['action']} page successfully.")
            print(json.dumps(result['result'], indent=2, ensure_ascii=False))

        elif args.command == 'tags':
            tags = client.list_tags()
            for tag in tags:
                print(f"  {tag['tag']}: {tag.get('title', '')}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
