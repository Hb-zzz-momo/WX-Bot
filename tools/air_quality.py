import httpx
from langchain.tools import tool


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def aqi_to_text(aqi: float) -> str:
    """
    将欧洲 AQI (EAQI) 换算成通俗的中文空气质量描述。
    """

    if aqi <= 20:
        return "优"
    if aqi <= 40:
        return "良"
    if aqi <= 60:
        return "轻度污染"
    if aqi <= 80:
        return "中度污染"
    if aqi <= 100:
        return "重度污染"

    return "严重污染"


@tool
def get_air_quality(city: str) -> str:
    """
    查询指定城市的空气质量（AQI、PM2.5、PM10 等指标）。

    当用户询问“今天空气好不好”、“PM2.5 多少”、
    “适合跑步吗”等空气污染问题时使用。

    Args:
        city: 用户想查询的城市名称，例如“北京”、“杭州”。
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

        results = geo_response.json().get("results")

        if not results:
            return f"没有找到城市：{city}"

        location = results[0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        city_name = location.get("name", city)

        # =========================
        # Step 2：经纬度 → 空气质量
        # =========================

        air_response = httpx.get(
            AIR_QUALITY_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,

                "current": [
                    "european_aqi",
                    "pm10",
                    "pm2_5",
                    "nitrogen_dioxide",
                    "ozone",
                    "sulphur_dioxide",
                    "carbon_monoxide",
                ],

                "timezone": "auto",
            },
            timeout=10.0,
        )

        air_response.raise_for_status()

        current = air_response.json().get("current")

        if not current:
            return f"暂时没有获取到 {city_name} 的空气质量数据"

        # =========================
        # Step 3：生成 Tool Result
        # =========================

        aqi = current.get("european_aqi")
        pm25 = current.get("pm2_5")
        pm10 = current.get("pm10")
        no2 = current.get("nitrogen_dioxide")
        o3 = current.get("ozone")
        so2 = current.get("sulphur_dioxide")
        co = current.get("carbon_monoxide")

        aqi_text = aqi_to_text(aqi) if aqi is not None else "未知"

        lines = [
            f"城市：{city_name}",
            f"空气质量：{aqi_text}（AQI {aqi}）",
        ]

        details = []

        if pm25 is not None:
            details.append(f"PM2.5 {pm25} μg/m³")
        if pm10 is not None:
            details.append(f"PM10 {pm10} μg/m³")
        if o3 is not None:
            details.append(f"臭氧 {o3} μg/m³")
        if no2 is not None:
            details.append(f"二氧化氮 {no2} μg/m³")
        if so2 is not None:
            details.append(f"二氧化硫 {so2} μg/m³")
        if co is not None:
            details.append(f"一氧化碳 {co} μg/m³")

        if details:
            lines.append("指标：" + "，".join(details))

        return "\n".join(lines)

    except httpx.HTTPError as e:

        return f"空气质量服务请求失败：{str(e)}"

    except Exception as e:

        return f"空气质量查询发生异常：{str(e)}"
