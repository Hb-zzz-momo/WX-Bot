from wx4py import WeChatClient


def main():
    print("正在连接微信...")

    with WeChatClient(auto_connect=True) as wx:
        print("微信连接成功")

        result = wx.chat_window.send_to(
            "文件传输助手",
            "wx4py 连接成功！"
        )

        print("发送结果：", result)


if __name__ == "__main__":
    main()