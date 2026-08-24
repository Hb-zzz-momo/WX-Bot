from tools.search import web_search


def main():
    query = input(
        "请输入要搜索的问题："
    )

    result = web_search.invoke(
        {
            "query": query,
            "topic": "general",
        }
    )

    print("\n========== 搜索结果 ==========\n")

    print(result)


if __name__ == "__main__":
    main()