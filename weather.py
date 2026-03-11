"""
weather.py - 天气信息获取（增强版）
支持：体感温度、日出日落、紫外线指数、湿度等
"""
import requests
from config import QWEATHER_API_KEY, QWEATHER_API_HOST

WEATHER_EMOJI = {
    "晴": "☀️", "多云": "⛅", "阴": "☁️", "少云": "🌤️", "晴间多云": "🌤️",
    "小雨": "🌧️", "中雨": "🌧️", "大雨": "🌧️", "暴雨": "🌊",
    "阵雨": "🌦️", "雷阵雨": "⛈️",
    "雨夹雪": "🌨️", "小雪": "❄️", "中雪": "❄️", "大雪": "❄️", "暴雪": "🌨️",
    "雾": "🌫️", "薄雾": "🌫️", "霾": "😷", "扬沙": "💨",
}

def _get_weather_qweather(city_id: str) -> dict:
    """和风天气 API（主要来源，含丰富细节）"""
    base_url = f"{QWEATHER_API_HOST}/v7"
    params = {"location": city_id, "key": QWEATHER_API_KEY}

    # 1. 获取实时天气 (用于体感温度 feelsLike)
    now_resp = requests.get(f"{base_url}/weather/now", params=params, timeout=10)
    now_resp.raise_for_status()
    now_data = now_resp.json()
    if now_data.get("code") != "200":
        raise RuntimeError(f"和风 now_code={now_data.get('code')}")

    now = now_data["now"]
    weather_text = now.get("text", "未知")
    emoji = WEATHER_EMOJI.get(weather_text, "🌈")

    # 2. 获取3天预报 (用于日出、日落、紫外线、最高/最低温)
    daily_resp = requests.get(f"{base_url}/weather/3d", params=params, timeout=10)
    daily_resp.raise_for_status()
    daily_data = daily_resp.json()

    # 默认值
    temp_min, temp_max = now.get("temp", "--"), now.get("temp", "--")
    sunrise, sunset = "--", "--"
    uv_index = "--"

    if daily_data.get("code") == "200" and daily_data.get("daily"):
        today = daily_data["daily"][0]
        temp_min = today.get("tempMin", temp_min)
        temp_max = today.get("tempMax", temp_max)
        sunrise = today.get("sunrise", "--")
        sunset = today.get("sunset", "--")
        uv_index = today.get("uvIndex", "--")

    return {
        "text": weather_text,
        "emoji": emoji,
        "temp": now.get("temp", "--"),
        "temp_min": temp_min,
        "temp_max": temp_max,
        "feels_like": now.get("feelsLike", "--"), # 这里确保键名是 feels_like
        "humidity": now.get("humidity", "--"),
        "wind_dir": now.get("windDir", "--"),
        "wind_scale": now_data["now"].get("windScale", "--"),
        "sunrise": sunrise,
        "sunset": sunset,
        "uv_index": uv_index,
        "source": "和风天气",
    }

def _get_weather_china(city_id: str) -> dict:
    """中国天气网（备用源：不含日出日落和体感）"""
    url = f"http://t.weather.itboy.net/api/weather/city/{city_id}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    
    info = data.get("data", {})
    forecast = info.get("forecast", [{}])
    today = forecast[0] if forecast else {}
    weather_type = today.get("type", "未知")
    
    # 清理温度字符串
    high = today.get("high", "--").replace("高温 ", "").replace("℃", "").strip()
    low = today.get("low", "--").replace("低温 ", "").replace("℃", "").strip()

    return {
        "text": weather_type,
        "emoji": WEATHER_EMOJI.get(weather_type, "🌈"),
        "temp": info.get("wendu", "--"),
        "temp_min": low,
        "temp_max": high,
        "feels_like": info.get("wendu", "--"), # 备用源用实时温度模拟体感
        "humidity": info.get("shidu", "--"),
        "wind_dir": today.get("fx", "--"),
        "wind_scale": today.get("fl", "--"),
        "sunrise": "--",
        "sunset": "--",
        "uv_index": "--",
        "source": "中国天气网",
    }

def get_weather(city_id: str) -> dict:
    """获取天气的主入口"""
    try:
        # 只要 QWEATHER_API_KEY 配置了，就优先尝试和风
        if QWEATHER_API_KEY and QWEATHER_API_KEY != "":
            return _get_weather_qweather(city_id)
    except Exception as e:
        print(f"   ⚠️ 和风天气获取失败: {e}，正在尝试备用源...")
    
    return _get_weather_china(city_id)
