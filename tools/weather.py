import httpx

from langchain.tools import tool


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def weather_code_to_text(code: int) -> str:
    """
    将 Open-Meteo weather code 转换成简单中文描述。
    """

    weather_codes = {
        0: "晴朗",
        1: "大致晴朗",
        2: "局部多云",
        3: "阴天",
        45: "有雾",
        48: "雾凇",
        51: "小毛毛雨",
        53: "中等毛毛雨",
        55: "较强毛毛雨",
        61: "小雨",
        63: "中雨",
        65: "大雨",
        71: "小雪",
        73: "中雪",
        75: "大雪",
        80: "小阵雨",
        81: "中等阵雨",
        82: "强阵雨",
        95: "雷暴",
        96: "雷暴并伴有小冰雹",
        99: "雷暴并伴有强冰雹",
    }

    return weather_codes.get(code, f"未知天气代码 {code}")


@tool
def get_weather(city: str) -> str:
    """
    查询指定城市当前的实时天气。

    当用户询问某个城市当前天气、气温、降雨、风速等实时天气信息时，
    应该使用这个工具。

    Args:
        city: 用户想查询天气的城市名称，例如“东京”、“温州”、“杭州”。
    """

    try:

        # =========================
        # Step 1：城市 → 经纬度
        # =========================

        geo_response = httpx.get(
            GEOCODING_URL,
            params={
                "name": city,
                "count": 1,
                "language": "zh",
                "format": "json",
            },
            timeout=10.0,
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        results = geo_data.get("results")

        if not results:
            return f"没有找到城市：{city}"

        location = results[0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        city_name = location.get("name", city)
        country = location.get("country", "")
        admin1 = location.get("admin1", "")

        # =========================
        # Step 2：经纬度 → 天气
        # =========================

        weather_response = httpx.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,

                "current": [
                    "temperature_2m",
                    "apparent_temperature",
                    "precipitation",
                    "weather_code",
                    "wind_speed_10m",
                ],

                "timezone": "auto",
            },
            timeout=10.0,
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = weather_data.get("current")

        if not current:
            return f"暂时没有获取到 {city_name} 的天气数据"

        # =========================
        # Step 3：提取天气
        # =========================

        temperature = current.get("temperature_2m")
        apparent_temperature = current.get(
            "apparent_temperature"
        )

        precipitation = current.get(
            "precipitation"
        )

        wind_speed = current.get(
            "wind_speed_10m"
        )

        weather_code = current.get(
            "weather_code"
        )

        weather_text = weather_code_to_text(
            weather_code
        )

        # =========================
        # Step 4：生成 Tool Result
        # =========================

        return (
            f"地点：{city_name} {admin1} {country}\n"
            f"天气：{weather_text}\n"
            f"气温：{temperature}℃\n"
            f"体感温度：{apparent_temperature}℃\n"
            f"降水量：{precipitation} mm\n"
            f"风速：{wind_speed} km/h"
        )

    except httpx.HTTPError as e:

        return (
            f"天气服务请求失败：{str(e)}"
        )

    except Exception as e:

        return (
            f"天气查询发生异常：{str(e)}"
        )