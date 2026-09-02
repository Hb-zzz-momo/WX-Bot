from context_engine.models import ContextItem
from context_engine.selector import select_group_context

from context_engine.builder import (
    build_group_context,
)

items = [
    ContextItem(
        content="张三：今晚吃火锅吗",
        source="group_chat",
        trust_level="untrusted",
        timestamp="2026-09-02 10:00:00",
    ),

    ContextItem(
        content="李四：杭州周六上午9点西湖集合",
        source="group_chat",
        trust_level="untrusted",
        timestamp="2026-09-02 10:01:00",
    ),

    ContextItem(
        content="王五：晚上打王者",
        source="group_chat",
        trust_level="untrusted",
        timestamp="2026-09-02 10:02:00",
    ),
]

selected = select_group_context(
    items,
    query="杭州周六几点集合？",
)

for item in selected:
    print(
        item.relevance_score,
        item.content,
    )
    
print(
    build_group_context(
        selected
    )
)