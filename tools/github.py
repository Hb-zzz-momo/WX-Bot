import os
from typing import Literal

import httpx

from dotenv import load_dotenv
from langchain.tools import tool


load_dotenv()


GITHUB_API_URL = "https://api.github.com"

GITHUB_API_VERSION = "2026-03-10"


def get_github_headers(
    accept: str = "application/vnd.github+json",
) -> dict:

    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Accept": accept,

        "X-GitHub-Api-Version":
            GITHUB_API_VERSION,

        "User-Agent": "WX-Bot",
    }

    # 没有 Token 也允许查询公开仓库
    if token:
        headers["Authorization"] = (
            f"Bearer {token}"
        )

    return headers

@tool
def github_search_repositories(
    query: str,
    sort: Literal[
        "stars",
        "forks",
        "updated",
    ] = "stars",
    limit: int = 5,
) -> str:
    """
    搜索 GitHub 仓库。

    当用户想寻找 GitHub 项目、开源项目、
    某一技术相关仓库时使用。

    query 支持 GitHub 搜索语法，例如：

    wechat bot language:python
    langgraph stars:>1000
    topic:llm-agent language:python

    Args:
        query:
            GitHub 仓库搜索关键词。

        sort:
            排序方式：
            stars、forks 或 updated。

        limit:
            返回项目数量。
    """

    try:

        limit = max(
            1,
            min(limit, 10)
        )

        response = httpx.get(
            f"{GITHUB_API_URL}/search/repositories",

            headers=get_github_headers(),

            params={
                "q": query,
                "sort": sort,
                "order": "desc",
                "per_page": limit,
            },

            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        repositories = data.get(
            "items",
            []
        )

        if not repositories:

            return (
                f"没有搜索到与「{query}」"
                f"相关的 GitHub 项目。"
            )

        results = []

        for index, repo in enumerate(
            repositories,
            start=1,
        ):

            results.append(
                f"""
项目 {index}

仓库：
{repo["full_name"]}

简介：
{repo.get("description") or "暂无简介"}

主要语言：
{repo.get("language") or "未知"}

Stars：
{repo.get("stargazers_count", 0)}

Forks：
{repo.get("forks_count", 0)}

Open Issues：
{repo.get("open_issues_count", 0)}

最近更新时间：
{repo.get("updated_at")}

GitHub：
{repo.get("html_url")}
""".strip()
            )

        return "\n\n".join(results)

    except httpx.HTTPStatusError as e:

        return (
            "GitHub API 请求失败："
            f"{e.response.status_code}"
        )

    except Exception as e:

        return (
            f"GitHub 搜索异常：{e}"
        )
        
@tool
def github_get_repository(
    owner: str,
    repo: str,
) -> str:
    """
    获取一个 GitHub 仓库的详细信息。

    当用户提供明确的 owner/repo，
    并希望了解该项目的 stars、forks、
    语言、许可证、更新时间等信息时使用。

    Args:
        owner:
            GitHub 用户名或组织名。

        repo:
            GitHub 仓库名。
    """

    try:

        response = httpx.get(
            f"{GITHUB_API_URL}/repos/{owner}/{repo}",

            headers=get_github_headers(),

            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        license_info = data.get(
            "license"
        )

        license_name = (
            license_info.get("spdx_id")
            if license_info
            else "未知"
        )

        topics = data.get(
            "topics",
            []
        )

        return f"""
仓库：
{data["full_name"]}

简介：
{data.get("description") or "暂无简介"}

Stars：
{data.get("stargazers_count", 0)}

Forks：
{data.get("forks_count", 0)}

Open Issues：
{data.get("open_issues_count", 0)}

主要语言：
{data.get("language") or "未知"}

License：
{license_name}

Topics：
{", ".join(topics) if topics else "暂无"}

默认分支：
{data.get("default_branch")}

创建时间：
{data.get("created_at")}

最近更新：
{data.get("updated_at")}

最近代码提交：
{data.get("pushed_at")}

GitHub：
{data.get("html_url")}
""".strip()

    except httpx.HTTPStatusError as e:

        if e.response.status_code == 404:

            return (
                f"没有找到仓库："
                f"{owner}/{repo}"
            )

        return (
            "GitHub API 请求失败："
            f"{e.response.status_code}"
        )

    except Exception as e:

        return (
            f"查询 GitHub 仓库失败：{e}"
        )
        
@tool
def github_get_readme(
    owner: str,
    repo: str,
) -> str:
    """
    获取指定 GitHub 仓库的 README。

    当用户希望了解项目是什么、
    如何安装、如何使用、技术架构、
    使用示例时应该使用。

    Args:
        owner:
            GitHub 用户或组织。

        repo:
            仓库名。
    """

    try:

        response = httpx.get(
            (
                f"{GITHUB_API_URL}"
                f"/repos/{owner}/{repo}/readme"
            ),

            headers=get_github_headers(
                accept=
                "application/vnd.github.raw+json"
            ),

            timeout=15.0,
        )

        response.raise_for_status()

        readme = response.text

        # 避免 README 太大导致 Token 爆炸
        MAX_LENGTH = 12000

        if len(readme) > MAX_LENGTH:

            readme = (
                readme[:MAX_LENGTH]
                +
                "\n\n[README 内容过长，已截断]"
            )

        return (
            f"仓库：{owner}/{repo}\n\n"
            f"README：\n\n"
            f"{readme}"
        )

    except httpx.HTTPStatusError as e:

        if e.response.status_code == 404:

            return (
                f"{owner}/{repo} "
                "没有找到 README。"
            )

        return (
            "读取 GitHub README 失败："
            f"{e.response.status_code}"
        )

    except Exception as e:

        return (
            f"README读取异常：{e}"
        )
        
@tool
def github_get_contents(
    owner: str,
    repo: str,
    path: str = "",
) -> str:
    """
    查看 GitHub 仓库中的目录或文件列表。

    当用户想查看项目结构、
    根目录、某个文件夹内容时使用。

    Args:
        owner:
            GitHub 用户或组织。

        repo:
            仓库名称。

        path:
            仓库目录路径。
            空字符串代表仓库根目录。
    """

    try:

        url = (
            f"{GITHUB_API_URL}"
            f"/repos/{owner}/{repo}/contents/{path}"
        )

        response = httpx.get(
            url,
            headers=get_github_headers(),
            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, list):

            lines = [
                f"仓库目录：{owner}/{repo}/{path}",
                "",
            ]

            for item in data:

                icon = (
                    "📁"
                    if item["type"] == "dir"
                    else "📄"
                )

                lines.append(
                    f"{icon} {item['path']}"
                )

            return "\n".join(lines)

        return (
            f"文件：{data.get('path')}\n"
            f"类型：{data.get('type')}\n"
            f"大小：{data.get('size')} bytes\n"
            f"GitHub：{data.get('html_url')}"
        )

    except httpx.HTTPStatusError as e:

        return (
            "读取 GitHub 仓库目录失败："
            f"{e.response.status_code}"
        )

    except Exception as e:

        return (
            f"GitHub目录查询异常：{e}"
        )


@tool
def github_list_issues(
    owner: str,
    repo: str,
    state: Literal[
        "open",
        "closed",
    ] = "open",
    limit: int = 5,
) -> str:
    """
    获取 GitHub 仓库的 Issues 列表。

    当用户想了解某个项目的
    问题讨论、Bug 反馈、待办事项、
    社区需求时使用。

    Args:
        owner:
            GitHub 用户名或组织名。

        repo:
            GitHub 仓库名。

        state:
            Issues 状态：open 或 closed。

        limit:
            返回 Issues 数量。
    """

    try:

        limit = max(
            1,
            min(limit, 10)
        )

        response = httpx.get(
            (
                f"{GITHUB_API_URL}"
                f"/repos/{owner}/{repo}/issues"
            ),

            headers=get_github_headers(),

            params={
                "state": state,
                "sort": "created",
                "direction": "desc",
                "per_page": limit,
            },

            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        # 排除 Pull Requests，只保留 Issues
        data = [
            item
            for item in data
            if not item.get("pull_request")
        ]

        if not data:

            state_text = (
                "已关闭" if state == "closed"
                else "未关闭"
            )

            return (
                f"{owner}/{repo} 目前没有{state_text}"
                "的 Issues。"
            )

        results = []

        for index, issue in enumerate(
            data,
            start=1,
        ):

            labels = issue.get(
                "labels",
                []
            )

            label_names = "、".join(
                label.get("name", "")
                for label in labels
                if isinstance(label, dict)
            )

            state_text = (
                "已关闭"
                if issue.get("state") == "closed"
                else "开放"
            )

            results.append(
                f"""
Issue {index}

标题：
{issue["title"]}

状态：
{state_text}

作者：
{issue["user"]["login"]}

标签：
{label_names or "暂无"}

创建时间：
{issue.get("created_at")}

评论数：
{issue.get("comments", 0)}

GitHub：
{issue.get("html_url")}
""".strip()
            )

        return "\n\n".join(results)

    except httpx.HTTPStatusError as e:

        if e.response.status_code == 404:

            return (
                f"没有找到仓库："
                f"{owner}/{repo}"
            )

        return (
            "GitHub API 请求失败："
            f"{e.response.status_code}"
        )

    except Exception as e:

        return (
            f"GitHub Issues 查询异常：{e}"
        )


@tool
def github_list_pull_requests(
    owner: str,
    repo: str,
    state: Literal[
        "open",
        "closed",
    ] = "open",
    limit: int = 5,
) -> str:
    """
    获取 GitHub 仓库的 Pull Requests 列表。

    当用户想了解某个项目的
    PR 讨论、代码审查进展、
    未被合并的改动时使用。

    Args:
        owner:
            GitHub 用户名或组织名。

        repo:
            GitHub 仓库名。

        state:
            PR 状态：open 或 closed。

        limit:
            返回 Pull Requests 数量。
    """

    try:

        limit = max(
            1,
            min(limit, 10)
        )

        response = httpx.get(
            (
                f"{GITHUB_API_URL}"
                f"/repos/{owner}/{repo}/pulls"
            ),

            headers=get_github_headers(),

            params={
                "state": state,
                "sort": "created",
                "direction": "desc",
                "per_page": limit,
            },

            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        if not data:

            state_text = (
                "已关闭" if state == "closed"
                else "未合并"
            )

            return (
                f"{owner}/{repo} 目前没有{state_text}"
                "的 Pull Requests。"
            )

        results = []

        for index, pull in enumerate(
            data,
            start=1,
        ):

            merge_state = (
                "已合并"
                if pull.get("merged")
                else (
                    "已关闭"
                    if pull.get("state") == "closed"
                    else "开放"
                )
            )

            results.append(
                f"""
PR {index}

标题：
{pull["title"]}

#{pull["number"]} - {merge_state}

作者：
{pull["user"]["login"]}

创建时间：
{pull.get("created_at")}

评论数：
{pull.get("comments", 0)}

变更：
+{pull.get("additions", 0)} / -{pull.get("deletions", 0)}

GitHub：
{pull.get("html_url")}
""".strip()
            )

        return "\n\n".join(results)

    except httpx.HTTPStatusError as e:

        if e.response.status_code == 404:

            return (
                f"没有找到仓库："
                f"{owner}/{repo}"
            )

        return (
            "GitHub API 请求失败："
            f"{e.response.status_code}"
        )

    except Exception as e:

        return (
            f"GitHub Pull Requests 查询异常：{e}"
        )


@tool
def github_list_commits(
    owner: str,
    repo: str,
    path: str = "",
    limit: int = 5,
) -> str:
    """
    获取 GitHub 仓库的提交记录。

    当用户想了解项目最近提交、
    某文件的历史改动、
    项目活跃度时使用。

    Args:
        owner:
            GitHub 用户名或组织名。

        repo:
            GitHub 仓库名。

        path:
            只查看某个文件或目录的提交。
            空字符串代表全部提交。

        limit:
            返回提交数量。
    """

    try:

        limit = max(
            1,
            min(limit, 10)
        )

        params = {
            "per_page": limit,
        }

        if path:
            params["path"] = path

        response = httpx.get(
            (
                f"{GITHUB_API_URL}"
                f"/repos/{owner}/{repo}/commits"
            ),

            headers=get_github_headers(),

            params=params,

            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        if not data:

            return (
                f"{owner}/{repo} 暂无提交记录。"
            )

        results = []

        for index, commit in enumerate(
            data,
            start=1,
        ):

            detail = commit.get(
                "commit",
                {}
            )

            author = commit.get(
                "author"
            )

            author_name = (
                author.get("login")
                if author
                else None
            )

            if not author_name:
                author_name = detail.get(
                    "author",
                    {}
                ).get("name")

            message = detail.get(
                "message",
                ""
            ).replace(
                "\n",
                " "
            ).strip()

            if len(message) > 300:
                message = (
                    message[:300] + "..."
                )

            results.append(
                f"""
提交 {index}

SHA：
{commit["sha"][:10]}

作者：
{author_name or "未知"}

时间：
{detail.get("author", {}).get("date")}

Message：
{message}

GitHub：
{commit.get("html_url")}
""".strip()
            )

        return "\n\n".join(results)

    except httpx.HTTPStatusError as e:

        if e.response.status_code == 404:

            target = (
                f"文件/路径：{path}"
                if path
                else (
                    f"{owner}/{repo} "
                    "没有找到仓库"
                )
            )

            return target

        return (
            "GitHub API 请求失败："
            f"{e.response.status_code}"
        )

    except Exception as e:

        return (
            f"GitHub Commits 查询异常：{e}"
        )


@tool
def github_list_releases(
    owner: str,
    repo: str,
    limit: int = 5,
) -> str:
    """
    获取 GitHub 仓库的版本发布记录。

    当用户想了解项目最新版本、
    更新日志、下载包、
    版本历史时使用。

    Args:
        owner:
            GitHub 用户名或组织名。

        repo:
            GitHub 仓库名。

        limit:
            返回 Release 数量。
    """

    try:

        limit = max(
            1,
            min(limit, 10)
        )

        response = httpx.get(
            (
                f"{GITHUB_API_URL}"
                f"/repos/{owner}/{repo}/releases"
            ),

            headers=get_github_headers(),

            params={
                "per_page": limit,
            },

            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        if not data:

            return (
                f"{owner}/{repo} 暂时没有发布版本。"
            )

        results = []

        for index, release in enumerate(
            data,
            start=1,
        ):

            body = release.get(
                "body"
            ) or "暂无说明"

            if len(body) > 800:
                body = (
                    body[:800]
                    + "\n\n[更新说明过长，已截断]"
                )

            results.append(
                f"""
发布 {index}

版本：
{release.get("tag_name")}

发布名：
{release.get("name") or "无"}

日期：
{release.get("published_at") or release.get("created_at")}

作者：
{release.get("author", {}).get("login")}

说明：
{body}

下载地址：
{release.get("html_url")}
""".strip()
            )

        return "\n\n".join(results)

    except httpx.HTTPStatusError as e:

        if e.response.status_code == 404:

            return (
                f"没有找到仓库："
                f"{owner}/{repo}"
            )

        return (
            "GitHub API 请求失败："
            f"{e.response.status_code}"
        )

    except Exception as e:

        return (
            f"GitHub Releases 查询异常：{e}"
        )


@tool
def github_list_contributors(
    owner: str,
    repo: str,
    limit: int = 5,
) -> str:
    """
    获取 GitHub 仓库的贡献者列表。

    当用户想知道谁参与了项目、
    Top 贡献者排名时使用。

    Args:
        owner:
            GitHub 用户名或组织名。

        repo:
            GitHub 仓库名。

        limit:
            返回贡献者数量。
    """

    try:

        limit = max(
            1,
            min(limit, 10)
        )

        response = httpx.get(
            (
                f"{GITHUB_API_URL}"
                f"/repos/{owner}/{repo}/contributors"
            ),

            headers=get_github_headers(),

            params={
                "per_page": limit,
            },

            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        if not data:

            return (
                f"{owner}/{repo} 暂无贡献者数据。"
            )

        results = []

        for index, contributor in enumerate(
            data,
            start=1,
        ):

            results.append(
                f"""
贡献者 {index}

用户名：
{contributor["login"]}

提交数：
{contributor.get("contributions", 0)}

头像资料：
{contributor.get("html_url")}
""".strip()
            )

        return "\n\n".join(results)

    except httpx.HTTPStatusError as e:

        if e.response.status_code == 404:

            return (
                f"没有找到仓库："
                f"{owner}/{repo}"
            )

        return (
            "GitHub API 请求失败："
            f"{e.response.status_code}"
        )

    except Exception as e:

        return (
            f"GitHub Contributors 查询异常：{e}"
        )


@tool
def github_get_languages(
    owner: str,
    repo: str,
) -> str:
    """
    获取 GitHub 仓库的语言构成。

    当用户想了解项目
    使用了哪些编程语言及比例时使用。

    Args:
        owner:
            GitHub 用户名或组织名。

        repo:
            GitHub 仓库名。
    """

    try:

        response = httpx.get(
            (
                f"{GITHUB_API_URL}"
                f"/repos/{owner}/{repo}/languages"
            ),

            headers=get_github_headers(),

            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        if not data:

            return (
                f"{owner}/{repo} 暂未检测到语言。"
            )

        total = sum(
            data.values()
        )

        items = sorted(
            data.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        lines = [
            (
                f"仓库语言构成："
                f"{owner}/{repo}"
            ),
            "",
        ]

        for index, (
            language,
            size,
        ) in enumerate(items, start=1):

            percent = (
                size * 100 / total
            )

            lines.append(
                f"{index}. {language} "
                f"({percent:.1f}%)"
            )

        return "\n".join(lines)

    except httpx.HTTPStatusError as e:

        if e.response.status_code == 404:

            return (
                f"没有找到仓库："
                f"{owner}/{repo}"
            )

        return (
            "GitHub API 请求失败："
            f"{e.response.status_code}"
        )

    except Exception as e:

        return (
            f"GitHub 语言查询异常：{e}"
        )


@tool
def github_search_code(
    query: str,
    limit: int = 5,
) -> str:
    """
    在 GitHub 全站搜索代码。

    当用户需要找某段代码、
    某个函数实现、
    某种写法的开源示例时使用。

    代码搜索需要配置 GITHUB_TOKEN。

    Args:
        query:
            代码搜索关键词，
            例如：def create_wechat_agent
            repo:langchain-ai/langgraph。

        limit:
            返回结果数量。
    """

    try:

        limit = max(
            1,
            min(limit, 10)
        )

        response = httpx.get(
            f"{GITHUB_API_URL}/search/code",

            headers=get_github_headers(),

            params={
                "q": query,
                "per_page": limit,
            },

            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("items"):

            return (
                f"没有搜索到与「{query}」"
                "相关的代码。"
            )

        results = []

        for index, item in enumerate(
            data["items"],
            start=1,
        ):

            repository = item.get(
                "repository",
                {},
            )

            results.append(
                f"""
代码结果 {index}

仓库：
{repository.get("full_name")}

文件：
{item.get("path")}

GitHub：
{item.get("html_url")}
""".strip()
            )

        total_count = data.get(
            "total_count",
            0
        )

        return (
            f"共找到 {total_count} 个结果，"
            f"展示前 {len(results)} 个：\n\n"
            + "\n\n".join(results)
        )

    except httpx.HTTPStatusError as e:

        status = e.response.status_code

        if status in (401, 403):

            return (
                "GitHub 代码搜索需要配置 "
                "GITHUB_TOKEN 后才能使用，"
                "请检查 .env 中的 Token。"
            )

        return (
            "GitHub API 请求失败："
            f"{status}"
        )

    except Exception as e:

        return (
            f"GitHub 代码搜索异常：{e}"
        )


@tool
def github_get_file_content(
    owner: str,
    repo: str,
    path: str,
) -> str:
    """
    获取 GitHub 仓库中某个文件的代码内容。

    当用户想查看具体文件的代码、
    README 之外的源码内容时使用。

    与目录列表不同，
    本工具返回文件的实际内容。

    Args:
        owner:
            GitHub 用户名或组织名。

        repo:
            GitHub 仓库名。

        path:
            文件的完整路径，
            例如：src/main.py。
    """

    try:

        url = (
            f"{GITHUB_API_URL}"
            f"/repos/{owner}/{repo}/contents/{path}"
        )

        response = httpx.get(
            url,

            headers=get_github_headers(
                accept=
                "application/vnd.github.raw+json"
            ),

            timeout=15.0,
        )

        response.raise_for_status()

        content = response.text

        # 避免文件太大导致 Token 爆炸
        MAX_LENGTH = 12000

        if len(content) > MAX_LENGTH:

            content = (
                content[:MAX_LENGTH]
                + "\n\n[文件内容过长，已截断]"
            )

        return (
            f"仓库：{owner}/{repo}\n\n"
            f"文件：{path}\n\n"
            f"内容：\n\n"
            f"{content}"
        )

    except httpx.HTTPStatusError as e:

        if e.response.status_code == 404:

            return (
                f"{owner}/{repo} 中"
                f"未找到文件：{path}"
            )

        return (
            "读取 GitHub 文件内容失败："
            f"{e.response.status_code}"
        )

    except Exception as e:

        return (
            f"GitHub 文件内容读取异常：{e}"
        )