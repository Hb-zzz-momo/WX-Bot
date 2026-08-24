import os
from typing import Literal

from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient


load_dotenv()


def get_tavily_client() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError(
            "没有找到 TAVILY_API_KEY，请检查 .env"
        )

    return TavilyClient(api_key=api_key)


@tool
def web_search(
    query: str,
    topic: Literal["general", "news"] = "general",
) -> str:
    """
    搜索互联网获取最新或实时信息。

    当用户询问最新新闻、当前事件、最近更新、
    某个产品或公司的最新动态，或者模型无法确定
    当前事实时，应使用这个工具。

    Args:
        query: 要搜索的具体问题或关键词。
        topic:
            general 表示普通网页搜索；
            news 表示新闻类搜索。
    """

    try:
        client = get_tavily_client()

        response = client.search(
            query=query,
            topic=topic,
            search_depth="basic",
            max_results=5,
        )

        results = response.get("results", [])

        if not results:
            return f"没有搜索到与「{query}」相关的结果。"

        formatted_results = []

        for index, result in enumerate(
            results,
            start=1
        ):
            title = result.get(
                "title",
                "无标题"
            )

            url = result.get(
                "url",
                ""
            )

            content = result.get(
                "content",
                ""
            )

            formatted_results.append(
                f"""
结果 {index}
标题：{title}
链接：{url}
摘要：{content}
""".strip()
            )

        return "\n\n".join(
            formatted_results
        )

    except Exception as e:
        return (
            f"网络搜索失败：{str(e)}"
        )