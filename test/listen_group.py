from wx4py import CallbackHandler, WeChatClient


GROUP_NAME = "我和我老婆"


def on_message(event):
    print("=" * 50)
    print("收到微信群消息")
    print("群聊：", event.group)
    print("内容：", event.content)
    print("=" * 50)


def main():
    print("正在启动微信群监听...")
    print(f"监听群聊：{GROUP_NAME}")

    with WeChatClient(auto_connect=True) as wx:
        print("微信连接成功")
        print("等待群消息...")
        print("按 Ctrl + C 可以停止机器人")

        wx.process_groups(
            [GROUP_NAME],
            [
                CallbackHandler(on_message)
            ],
            block=True,
        )


if __name__ == "__main__":
    main()