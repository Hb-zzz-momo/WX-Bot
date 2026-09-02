from types import SimpleNamespace

from langchain.messages import (
    HumanMessage,
    AIMessage,
)

from agent.context_middleware import (
    insert_data_before_latest_user_message,
)

from agent.context_middleware import (
    build_runtime_data_context
)

context = SimpleNamespace(
    group_name="微信Agent测试群",

    recent_group_context=(
        "[20:00] 张三："
        "杭州周六上午9点集合\n"
        "[20:01] 李四：收到"
    ),

    user_id=None,

    user_memory="",
)

print(
    build_runtime_data_context(
        context
    )
)

messages = [
    HumanMessage(
        content="之前的问题"
    ),

    AIMessage(
        content="之前回答"
    ),

    HumanMessage(
        content="杭州几点集合？"
    ),
]

data_message = HumanMessage(
    content="GROUP_CHAT_DATA..."
)

result = (
    insert_data_before_latest_user_message(
        messages,
        data_message,
    )
)
for message in result:

    print(
        type(message).__name__,
        "=>",
        message.content,
    )