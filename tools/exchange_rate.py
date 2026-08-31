import httpx
from langchain.tools import tool


EXCHANGE_RATE_URL = "https://open.er-api.com/v6/latest/USD"

CURRENCY_NAMES = {
    "CNY": "人民币",
    "USD": "美元",
    "EUR": "欧元",
    "JPY": "日元",
    "GBP": "英镑",
    "HKD": "港币",
    "KRW": "韩元",
    "AUD": "澳大利亚元",
    "CAD": "加拿大元",
    "SGD": "新加坡元",
    "THB": "泰铢",
    "RUB": "卢布",
    "NZD": "新西兰元",
    "CHF": "瑞士法郎",
}


def _normalize_currency(code: str) -> str:
    """
    将用户输入的中文货币名或英文代码统一为 ISO 货币代码。
    """

    name_to_code = {
        "人民币": "CNY", "元": "CNY", "rmb": "CNY", "cny": "CNY",
        "美元": "USD", "美金": "USD", "usd": "USD",
        "欧元": "EUR", "eur": "EUR",
        "日元": "JPY", "jpy": "JPY",
        "英镑": "GBP", "gbp": "GBP",
        "港币": "HKD", "港元": "HKD", "hkd": "HKD",
        "韩元": "KRW", "韩币": "KRW", "krw": "KRW",
        "澳元": "AUD", "澳大利亚元": "AUD", "aud": "AUD",
        "加元": "CAD", "加拿大元": "CAD", "cad": "CAD",
        "新加坡元": "SGD", "sgd": "SGD",
        "泰铢": "THB", "thb": "THB",
        "卢布": "RUB", "rub": "RUB",
        "新西兰元": "NZD", "nzd": "NZD",
        "瑞郎": "CHF", "瑞士法郎": "CHF", "chf": "CHF",
    }

    cleaned = code.strip().upper()

    if cleaned in name_to_code:
        return name_to_code[cleaned]

    return cleaned


@tool
def exchange_rate(
    amount: float = 1,
    from_currency: str = "CNY",
    to_currency: str = "USD",
) -> str:
    """
    实时汇率换算。

    当用户询问“1000人民币等于多少美元”、“1欧元值多少日元”
    等汇率问题时使用。

    Args:
        amount: 需要换算的金额，默认 1。
        from_currency: 源货币，支持代码（如 USD）或中文名（如美元），默认 CNY。
        to_currency: 目标货币，支持代码（如 EUR、CNY）或中文名，默认 USD。
    """

    try:
        response = httpx.get(
            EXCHANGE_RATE_URL,
            timeout=10.0,
        )

        response.raise_for_status()

        data = response.json()

        base = data.get("base_code", "USD")
        rates = data.get("rates", {})

        if not rates or data.get("result") != "success":
            return "汇率服务暂时不可用，请稍后再试。"

        src = _normalize_currency(from_currency)
        dst = _normalize_currency(to_currency)

        if src not in rates or dst not in rates:
            supported = "、".join(sorted(rates))
            return (
                f"不支持的货币代码：{src} 或 {dst}。"
                f"当前支持：{supported}"
            )

        rate = rates[dst] / rates[src]
        converted = amount * rate

        src_name = CURRENCY_NAMES.get(src, src)
        dst_name = CURRENCY_NAMES.get(dst, dst)

        return (
            f"{amount:g} {src_name}({src}) = "
            f"{converted:.2f} {dst_name}({dst})\n"
            f"汇率：1 {src} ≈ {rate:.4f} {dst}"
        )

    except httpx.HTTPError as e:

        return f"汇率服务请求失败：{str(e)}"

    except Exception as e:

        return f"汇率查询发生异常：{str(e)}"
