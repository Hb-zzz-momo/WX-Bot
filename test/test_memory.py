from agent.core import ask_agent


THREAD_ID = "persistent-test-001"


def main():

    print("SQLite Memory 测试")
    print("输入 exit 退出")

    while True:

        question = input("\n你：")

        if question.lower() == "exit":
            break

        answer = ask_agent(
            user_message=question,
            thread_id=THREAD_ID,
        )

        print("\nAgent：")
        print(answer)


if __name__ == "__main__":
    main()