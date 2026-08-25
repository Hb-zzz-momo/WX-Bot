from database.db import init_database


def main():

    init_database()

    print(
        "business.db 初始化完成"
    )


if __name__ == "__main__":
    main()