import sys

from database.db import init_database

from database.repository import (
    get_enabled_groups,
    upsert_group,
)


def show_groups():

    groups = get_enabled_groups()

    print("\n当前监听群：")

    if not groups:
        print("暂无")
        return

    for group in groups:

        ai_status = (
            "AI开启"
            if group["ai_enabled"]
            else "仅监听"
        )

        print(
            f"- {group['name']} | {ai_status}"
        )


def main():

    init_database()

    if len(sys.argv) < 2:

        print(
            """
使用方式：

python manage_groups.py list

python manage_groups.py add "微信群1"

python manage_groups.py listen-only "微信群2"

python manage_groups.py disable "微信群3"
"""
        )

        return

    command = sys.argv[1]

    if command == "list":

        show_groups()

        return

    if len(sys.argv) < 3:

        print("请提供群名称")

        return

    group_name = sys.argv[2]

    if command == "add":

        upsert_group(
            group_name,
            enabled=True,
            ai_enabled=True,
        )

        print(
            f"已添加：{group_name}"
        )

    elif command == "listen-only":

        upsert_group(
            group_name,
            enabled=True,
            ai_enabled=False,
        )

        print(
            f"仅监听：{group_name}"
        )

    elif command == "disable":

        upsert_group(
            group_name,
            enabled=False,
            ai_enabled=False,
        )

        print(
            f"已停用：{group_name}"
        )

    else:

        print(
            f"未知命令：{command}"
        )


if __name__ == "__main__":
    main() 