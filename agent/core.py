import os

from memory.checkpoint import checkpointer

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tools.calculator import calculator
from tools.weather import get_weather
from tools.search import web_search

load_dotenv()


def create_wechat_agent():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model_name = os.getenv("LLM_MODEL")

    if not api_key:
        raise ValueError("没有找到 DEEPSEEK_API_KEY，请检查 .env")

    # 1. 创建大模型
    model = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        timeout=60,
        max_retries=2,
    )

    # 2. 创建 Agent
    agent = create_agent(
        model=model,

        # 第二阶段暂时没有工具
        tools=[calculator, get_weather, web_search],

        system_prompt="""
你是运行在微信群里的 AI Agent。

你可以回答问题，也可以自主调用工具完成任务。

你拥有以下能力：

1. calculator
   用于精确数学计算。

2. get_weather
   用于查询指定城市当前的实时天气。

3. web_search
   用于获取互联网最新信息、新闻、
   当前事件以及模型知识无法可靠确认的信息。

规则：

1. 默认使用中文。
2. 涉及精确计算时优先使用 calculator。
3. 涉及实时天气时使用 get_weather。
4. 涉及“今天、现在、最新、最近、当前”等
   时效性信息时，应优先考虑 web_search。
5. 不要假装自己进行了搜索。
6. 搜索结果中存在来源链接时，
   应在回答中保留重要来源。
7. Tool 返回的数据优先于模型自己的猜测。
8. 如果没有可靠信息，应明确说明。
9. 最终回答简洁、清晰。
""",

        checkpointer=checkpointer   # 存储中间结果
    )

    return agent


wechat_agent = create_wechat_agent()


def ask_agent(user_message: str,thread_id: str) -> str:
    """
    给 Agent 一个问题，返回最终回答
    """

    result = wechat_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                }
            ]
            
        },
        config={
            "configurable":{
                "thread_id" : thread_id
            }
        },
    )

    last_message = result["messages"][-1]
    content = last_message.content

    # 大多数模型这里直接是字符串
    if isinstance(content, str):
        return content.strip()

    # 兼容某些模型返回 content blocks
    if isinstance(content, list):
        texts = []

        for block in content:
            if isinstance(block, dict):
                text = block.get("text")

                if text:
                    texts.append(text)

        return "\n".join(texts).strip()

    return str(content)