import os

import httpx
from dotenv import load_dotenv
from langchain.tools import tool


load_dotenv()

AMAP_URL = "https://restapi.amap.com/v3"


def get_amap_key() -> str:
    key = os.getenv("AMAP_API_KEY")

    if not key:
        raise ValueError(
            "没有找到 AMAP_API_KEY（高德地图开放平台），"
            "请到 https://lbs.amap.com 免费申请并在 .env 中配置"
        )

    return key


@tool
def get_ip_location() -> str:
    """
    获取机器人当前 IP 的大致位置（省/市）。

    当用户询问“附近有什么”、“我在这里……”等需要
    自动判断当前城市的问题时，先调用本工具定位城市，
    再把城市传给 find_poi_nearby。

    Returns:
        省、市、区、IP 所在地信息。
    """

    try:
        key = get_amap_key()

        response = httpx.get(
            f"{AMAP_URL}/ip",
            params={"key": key},
            timeout=10.0,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "1":
            return f"IP 定位失败：{data.get('info', '未知错误')}"

        province = data.get("province", "未知省")
        city = data.get("city", "未知市")
        adcode = data.get("adcode", "")

        return f"IP 定位：{province} {city}（adcode: {adcode}）"

    except httpx.HTTPError as e:

        return f"IP 定位服务请求失败：{str(e)}"

    except Exception as e:

        return f"IP 定位发生异常：{str(e)}"


@tool
def find_poi_nearby(keyword: str, city: str = "", limit: int = 10) -> str:
    """
    搜索地点（POI），如美食、餐厅、加油站、药店、快递站、地铁站等。

    当用户询问“附近有什么”、“推荐餐厅”、“哪里有加油站/药店/
    银行/便利店”等问题时使用。

    Args:
        keyword: 要搜索的地点类型或名称，例如“烧烤”“加油站”“药店”。
        city: 搜索所在城市，例如“杭州”；如果不填则尝试自动定位当前城市。
        limit: 最多返回多少个结果，默认 10 个，最大 20 个。
    """

    try:
        key = get_amap_key()

        params = {
            "key": key,
            "keywords": keyword,
            "offset": min(limit, 20),
            "page": 1,
            "extensions": "base",
            "citylimit": "true",
        }

        if city:
            params["city"] = city

        response = httpx.get(
            f"{AMAP_URL}/place/text",
            params=params,
            timeout=10.0,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "1":
            return f"地点搜索失败：{data.get('info', '未知错误')}"

        pois = data.get("pois", [])

        if not pois:
            city_note = f"在{city}中" if city else ""
            return f"没有在{city_note}找到「{keyword}」相关地点。"

        results = []

        for index, poi in enumerate(pois[:limit], start=1):
            name = poi.get("name", "未知")
            address = poi.get("address", "")
            pname = poi.get("pname", "")
            cityname = poi.get("cityname", "")
            adname = poi.get("adname", "")
            distance = poi.get("distance", "")

            location = poi.get("location", "")

            if distance:
                results.append(
                    f"{index}. {name}（距此约{distance}米）\n"
                    f"   地址：{pname}{cityname}{adname}{address}\n"
                    f"   经纬度：{location}"
                )
            else:
                results.append(
                    f"{index}. {name}\n"
                    f"   地址：{pname}{cityname}{adname}{address}\n"
                    f"   经纬度：{location}"
                )

        return "\n\n".join(results)

    except httpx.HTTPError as e:

        return f"地点搜索服务请求失败：{str(e)}"

    except Exception as e:

        return f"地点搜索发生异常：{str(e)}"


@tool
def geocode_location(address: str) -> str:
    """
    将给定地址转换成经纬度（高德坐标系）。

    当用户询问“某某地址在哪”、“某某地点坐标”、
    或需要地址对应的经纬度时使用。

    Args:
        address: 需要转换的街道地址或地名，例如“北京市朝阳区阜通东大街6号”。
    """

    try:
        key = get_amap_key()

        response = httpx.get(
            f"{AMAP_URL}/geocode/geo",
            params={"key": key, "address": address},
            timeout=10.0,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "1":
            return f"地址转换失败：{data.get('info', '未知错误')}"

        geocodes = data.get("geocodes", [])

        if not geocodes:
            return f"没有找到地址：{address}"

        geo = geocodes[0]

        formatted_address = geo.get("formatted_address", address)
        location = geo.get("location", "未知")
        level = geo.get("level", "")

        return (
            f"地址：{formatted_address}\n"
            f"经纬度：{location}\n"
            f"匹配级别：{level}"
        )

    except httpx.HTTPError as e:

        return f"地理位置服务请求失败：{str(e)}"

    except Exception as e:

        return f"地理位置转换发生异常：{str(e)}"
