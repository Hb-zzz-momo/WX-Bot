from wx4py import WeChatClient


GROUP_NAME = "我和我老婆"


def main():
    print("正在连接微信...")

    with WeChatClient(auto_connect=True) as wx:
        print("微信连接成功")

        result = wx.chat_window.send_to(
            GROUP_NAME,
            "🤖 微信 Agent 接入测试成功",
            target_type="group",
        )

        print("群消息发送结果：", result)


if __name__ == "__main__":
    main()