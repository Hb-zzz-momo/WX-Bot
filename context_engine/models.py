from dataclasses import dataclass


@dataclass
class ContextItem:
    """
    Agent Context 中的一条标准化信息。

    注意：
    ContextItem 不是最终 Prompt，
    而是进入 Selector / Builder 前的中间数据结构。
    """

    # 真正的信息内容
    content: str

    # 信息来自哪里
    # 例如：
    # group_chat
    # user_memory
    # github
    # web
    source: str

    # 信任等级
    # V1 暂时使用简单字符串，
    # 后续可以改成 Enum。
    trust_level: str

    # 数据产生时间
    timestamp: str | None = None

    # 和当前问题的相关性分数
    relevance_score: float = 0.0