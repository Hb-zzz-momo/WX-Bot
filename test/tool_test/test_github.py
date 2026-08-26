from tools.github import (
    github_search_repositories,
    github_get_repository,
    github_get_readme,
    github_get_contents,
    github_list_issues,
    github_list_pull_requests,
    github_list_commits,
    github_list_releases,
    github_list_contributors,
    github_get_languages,
    github_search_code,
    github_get_file_content,
)


print("========= 搜索 =========")

print(
    github_search_repositories.invoke(
        {
            "query":
                "wechat bot language:python",

            "sort":
                "stars",

            "limit":
                5,
        }
    )
)


print("\n========= 项目详情 =========")

print(
    github_get_repository.invoke(
        {
            "owner": "langchain-ai",
            "repo": "langgraph",
        }
    )
)


print("\n========= README =========")

print(
    github_get_readme.invoke(
        {
            "owner": "langchain-ai",
            "repo": "langgraph",
        }
    )
)


print("\n========= 项目结构 =========")

print(
    github_get_contents.invoke(
        {
            "owner": "langchain-ai",
            "repo": "langgraph",
            "path": "",
        }
    )
)


print("\n========= Issues =========")

print(
    github_list_issues.invoke(
        {
            "owner": "langchain-ai",
            "repo": "langgraph",
            "state": "open",
            "limit": 5,
        }
    )
)


print("\n========= Pull Requests =========")

print(
    github_list_pull_requests.invoke(
        {
            "owner": "langchain-ai",
            "repo": "langgraph",
            "state": "open",
            "limit": 5,
        }
    )
)


print("\n========= Commits =========")

print(
    github_list_commits.invoke(
        {
            "owner": "langchain-ai",
            "repo": "langgraph",
            "path": "",
            "limit": 5,
        }
    )
)


print("\n========= Releases =========")

print(
    github_list_releases.invoke(
        {
            "owner": "langchain-ai",
            "repo": "langgraph",
            "limit": 3,
        }
    )
)


print("\n========= Contributors =========")

print(
    github_list_contributors.invoke(
        {
            "owner": "langchain-ai",
            "repo": "langgraph",
            "limit": 5,
        }
    )
)


print("\n========= Languages =========")

print(
    github_get_languages.invoke(
        {
            "owner": "langchain-ai",
            "repo": "langgraph",
        }
    )
)


print("\n========= 代码搜索 =========")

print(
    github_search_code.invoke(
        {
            "query":
                "def create_wechat_agent "
                "language:python",
            "limit": 3,
        }
    )
)


print("\n========= 文件内容 =========")

print(
    github_get_file_content.invoke(
        {
            "owner": "langchain-ai",
            "repo": "langgraph",
            "path": "libs/langgraph/pyproject.toml",
        }
    )
)