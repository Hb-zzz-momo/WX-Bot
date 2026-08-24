from agent.core import wechat_agent


def main():

    print("Agent Debug 模式启动")

    while True:

        question = input("\n你：")

        if question.lower() in [
            "exit",
            "quit"
        ]:
            break

        result = wechat_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ]
            }
        )

        print("\n========== Agent执行过程 ==========")

        for message in result["messages"]:

            print(
                "\n消息类型：",
                type(message).__name__
            )

            print(
                "内容：",
                message.content
            )

            tool_calls = getattr(
                message,
                "tool_calls",
                None
            )

            if tool_calls:

                print(
                    "Tool Calls：",
                    tool_calls
                )

        print("\n========== 最终回答 ==========")

        print(
            result["messages"][-1].content
        )


if __name__ == "__main__":
    main()