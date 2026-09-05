import re

from langchain.messages import (
    HumanMessage,
)


# ==========================================
# 用户明确要求长期记忆的表达
# ==========================================

MEMORY_REQUEST_PATTERNS = [
    r"记住",
    r"帮我记住",
    r"以后记得",
    r"以后按照",
    r"以后都",
    r"长期记住",
    r"保存我的",
    r"记一下我的",
]


# ==========================================
# 明显不应该进入长期Memory的敏感信息
# ==========================================

SENSITIVE_PATTERNS = [
    r"password",
    r"passwd",
    r"密码",
    r"api[_ -]?key",
    r"access[_ -]?token",
    r"secret",
    r"私钥",
    r"private[_ -]?key",
]

FORGET_MEMORY_PATTERNS = [
    r"忘掉",
    r"忘记",
    r"不要记",
    r"删除.*记忆",
    r"清除.*记忆",
    r"取消.*记忆",
]

# ==========================================
# Memory Key Alias
# ==========================================

MEMORY_KEY_ALIASES = {
    # 回答风格
    "answer_style": "response_style",
    "reply_style": "response_style",
    "response_preference": "response_style",

    # 语言
    "language": "preferred_language",
    "language_preference": "preferred_language",

    # 称呼
    "nickname": "preferred_name",
    "call_me": "preferred_name",
}


def normalize_memory_key(
    memory_key: str,
) -> str:
    """
    将模型生成的 Memory Key
    尽可能标准化。

    V1只做：
    - lowercase
    - 空格/横线 → 下划线
    - alias映射
    """

    key = (
        memory_key
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )

    while "__" in key:
        key = key.replace(
            "__",
            "_",
        )

    return MEMORY_KEY_ALIASES.get(
        key,
        key,
    )

def get_latest_user_message(
    state,
) -> str:
    """
    从Graph State中获取最近一条
    真实HumanMessage。

    注意：
    Day5注入的Group Context是Transient Context，
    不会写进State，因此这里不会把群聊背景
    当成真实用户授权。
    """

    if not state:

        return ""

    messages = state.get(
        "messages",
        [],
    )

    for message in reversed(
        messages
    ):

        if isinstance(
            message,
            HumanMessage,
        ):

            content = (
                message.content
            )

            if isinstance(
                content,
                str,
            ):
                return (
                    content.strip()
                )

    return ""


def has_explicit_memory_request(
    user_message: str,
) -> bool:
    """
    判断当前用户是否明确要求长期记忆。
    """

    if not user_message:
        return False

    for pattern in (
        MEMORY_REQUEST_PATTERNS
    ):

        if re.search(
            pattern,
            user_message,
            re.IGNORECASE,
        ):
            return True

    return False


def contains_sensitive_data(
    value: str,
) -> bool:
    """
    简单检测不应长期保存的敏感凭据。
    """

    if not value:
        return False

    for pattern in (
        SENSITIVE_PATTERNS
    ):

        if re.search(
            pattern,
            value,
            re.IGNORECASE,
        ):
            return True

    return False

def has_explicit_forget_request(
    user_message: str,
) -> bool:

    if not user_message:
        return False

    for pattern in (
        FORGET_MEMORY_PATTERNS
    ):

        if re.search(
            pattern,
            user_message,
            re.IGNORECASE,
        ):
            return True

    return False

def validate_memory_payload(
    memory_key: str,
    memory_value: str,
) -> tuple[bool, str]:
    """
    Memory内容本身的基础校验。
    """

    key = memory_key.strip()
    value = memory_value.strip()

    if not key:

        return (
            False,
            "memory_key不能为空。",
        )

    if not value:

        return (
            False,
            "memory_value不能为空。",
        )

    # 防止模型生成巨大的Memory
    if len(key) > 64:

        return (
            False,
            "memory_key过长。",
        )

    if len(value) > 500:

        return (
            False,
            "长期记忆内容过长。",
        )

    if contains_sensitive_data(
        value
    ):

        return (
            False,
            "检测到敏感凭据信息，禁止写入长期记忆。",
        )

    return (
        True,
        "",
    )