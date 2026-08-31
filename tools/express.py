import base64
import hashlib
import json
import os

import httpx
from dotenv import load_dotenv
from langchain.tools import tool


load_dotenv()

KDNIAO_URL = "https://api.kdniao.com/api/dist"

# 快递鸟公司编码（官方编码表）
COMMON_COMPANIES = {
    "顺丰": "SF", "顺丰速运": "SF", "SF": "SF",
    "圆通": "YTO", "圆通速递": "YTO", "YUANTONG": "YTO",
    "中通": "ZTO", "ZHONGTONG": "ZTO",
    "韵达": "YD", "韵达快递": "YD", "YUNDA": "YD",
    "申通": "STO", "SHENTONG": "STO",
    "邮政": "YZPY", "邮政包裹": "YZPY",
    "EMS": "EMS",
    "京东": "JD", "京东物流": "JD", "JD": "JD",
    "极兔": "JTSD", "极兔速递": "JTSD", "JTEXPRESS": "JTSD",
    "百世": "BEST", "百世快递": "BEST",
    "德邦": "DBL", "德邦快递": "DBL", "DEBANGKUAIDI": "DBL",
    "天天": "TTPD", "天天快递": "TTPD",
}

STATE_TEXT = {
    "0": "无轨迹",
    "1": "已揽收",
    "2": "在途中",
    "3": "已签收",
    "4": "问题件",
}


def _normalize_company(name: str) -> str:
    cleaned = name.strip().upper()

    if cleaned in COMMON_COMPANIES:
        return COMMON_COMPANIES[cleaned]

    return name.strip()


def _sign(request_data: str, api_key: str) -> str:
    """
    快递鸟签名规则：base64( md5(requestData + apiKey) 大写 )
    """

    raw = hashlib.md5(
        (request_data + api_key).encode("utf-8")
    ).hexdigest().upper()

    return base64.b64encode(raw.encode("utf-8")).decode("utf-8")


@tool
def check_express(
    company: str,
    tracking_no: str,
) -> str:
    """
    实时查询快递物流轨迹。

    当用户询问“我的快递到哪了”、“快递状态”、
    或给出了快递单号时使用。

    Args:
        company: 快递公司名称，例如“顺丰”“圆通”“韵达”“EMS”“京东”。
        tracking_no: 快递单号。
    """

    try:
        ebusiness_id = os.getenv("KDNIAO_EBUSINESS_ID")
        api_key = os.getenv("KDNIAO_API_KEY")

        if not ebusiness_id or not api_key:
            return (
                "没有配置快递查询密钥（KDNIAO_EBUSINESS_ID / KDNIAO_API_KEY），"
                "请到 https://www.kdniao.com 申请后配置 .env"
            )

        normalized_company = _normalize_company(company)

        request_data = json.dumps(
            {
                "OrderCode": "",
                "ShipperCode": normalized_company,
                "LogisticCode": tracking_no,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )

        response = httpx.post(
            KDNIAO_URL,
            json={
                "EBusinessID": ebusiness_id,
                "RequestType": "8001",
                "RequestData": request_data,
                "DataType": "2",
                "DataSign": _sign(request_data, api_key),
            },
            timeout=10.0,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("Success") is not True:
            return f"快递查询失败：{data.get('Reason', '未知错误')}"

        traces = data.get("Traces") or []

        if not traces:
            return "暂时没有查询到该快递的物流轨迹，请稍后再试。"

        latest = traces[0]

        latest_text = latest.get("AcceptStation", "未知状态")
        latest_time = latest.get("AcceptTime", "")

        state = data.get("State", "")
        state_text = STATE_TEXT.get(state, state)

        lines = [
            f"单号：{tracking_no}",
            f"状态：{state_text}",
            f"最新：{latest_text}（{latest_time}）",
        ]

        history = []

        for item in traces[:5]:
            content = item.get("AcceptStation", "")
            accept_time = item.get("AcceptTime", "")

            if content:
                history.append(f"- {accept_time}：{content}")

        if history:
            lines.append("最近物流：")
            lines.extend(history)

        return "\n".join(lines)

    except httpx.HTTPError as e:

        return f"快递查询服务请求失败：{str(e)}"

    except Exception as e:

        return f"快递查询发生异常：{str(e)}"
