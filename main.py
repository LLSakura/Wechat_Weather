"""
main.py - PushPlus 群组推送（丰富天气 + 国际新闻 + Gemini 点评/情话 + 早晚安）

运行方式：
    python main.py                # 默认早安模式
    python main.py --mode evening  # 晚安模式
    python main.py --schedule      # 本地定时模式（不推荐在 GitHub Actions 使用）
"""
import argparse
import random
import sys
import time
from datetime import date, datetime

import schedule

from config import check_config, CITIES, MORNING_TIME, EVENING_TIME
from weather import get_weather
from love_message import generate_love_message
from push import send_message, build_html_content


GREETINGS = {
    "morning": [
        "🌞 早安啦~~ my darling",
        "🌞 小饼干，新的一天也要开心哦",
        "☀️ 起床啦，今天也要越来越爱我~！",
        "🌸 宝贝，又是想见你的一天",
        "❤ 新的一天开始啦，谁是我的puppy呀~",
    ],
    "evening": [
        "🌙 晚安安啦~ my darling~",
        "🌙 宝贝今天辛苦啦，要早点休息~",
        "✨ 晚安安啦，明天也会是爱你的一天呢~",
        "🌃 晚安安小饼干~ 梦到我吧~",
        "💫 晚安安啦，在梦里亲亲你~",
    ],
}


def push_once(mode: str = "morning"):
    """执行一次推送"""
    print("=" * 60)
    mode_label = "🌞 早安推送" if mode == "morning" else "🌙 晚安推送"
    print(f"🚀 {mode_label} — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    check_config()
    today = date.today().strftime("%Y-%m-%d")

    # 获取所有城市的天气
    weather_sections = []
    for city in CITIES:
        print(f"\n📍 获取 {city.person}（{city.city_name}）的天气...")
        try:
            w = get_weather(city.city_id)
            print(f"   {w['emoji']} {w['text']} {w['temp_min']}~{w['temp_max']}℃ 体感{w['feels_like']}℃")
            print(f"   💧 湿度{w['humidity']}%  💨 {w['wind_dir']}{w['wind_scale']}级")
            weather_sections.append(w | {"person": city.person, "city": city.city_name})
        except Exception as e:
            print(f"   ⚠️ 获取失败：{e}")
            weather_sections.append({
                "person": city.person, "city": city.city_name,
                "emoji": "🌈", "text": "未知",
                "temp_min": "--", "temp_max": "--",
                "feels_like": "--", "humidity": "--",
                "wind_dir": "--", "wind_scale": "--",
                "wind_speed": "--", "vis": "--", "pressure": "--",
                "sunrise": "--", "sunset": "--", "uv_index": "--",
            })

    # Gemini 生成：天气点评 + 国际新闻 + 英语情话
    print(f"\n💕 正在请 Gemini 生成...")
    try:
        gemini_result = generate_love_message(weather_sections, mode=mode, date_str=today)
    except Exception as e:
        print(f"   ❌ Gemini 调用异常: {e}")
        gemini_result = {}

    # 提取并设置兜底文本，防止字段缺失导致 build_html 出错
    comment = gemini_result.get("comment", "记得按时吃饭，照顾好自己。")
    news = gemini_result.get("news", "")
    love_msg = gemini_result.get("love", "You are the best thing that ever happened to me.")

    if comment:
        print(f"\n   📝 天气点评：{comment}")
    if news:
        print(f"   🌍 国际视点：{news}")
    print(f"   💌 英语情话：{love_msg}")

    # 随机选择问候语
    greeting_list = GREETINGS.get(mode, GREETINGS["morning"])
    greeting = random.choice(greeting_list)

    # 构建 HTML
    content = build_html_content(
        date_str=today,
        mode=mode,
        weather_sections=weather_sections,
        gemini_comment=comment,
        gemini_news=news,
        love_msg=love_msg,
        greeting=greeting,
    )

    # 推送标题
    title = f"❤️ 今天也是爱你的一天 · {today}"
    
    # 执行发送
    success = send_message(title=title, content=content)
    if success:
        print(f"\n✅ 推送成功！ -> 群组")
    else:
        print(f"\n❌ 推送失败，请检查 PushPlus 配置")

    print(f"\n{'=' * 60}\n")


def run_scheduled():
    print(f"⏰ 定时推送已启动")
    print(f"   🌞 早安：{MORNING_TIME}  🌙 晚安：{EVENING_TIME}")
    print(f"   按 Ctrl+C 停止\n")

    schedule.every().day.at(MORNING_TIME).do(push_once, mode="morning")
    schedule.every().day.at(EVENING_TIME).do(push_once, mode="evening")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    # 使用 argparse 获取 GitHub Actions 传来的 --mode 参数
    parser = argparse.ArgumentParser(description="微信每日推送")
    parser.add_argument("--schedule", action="store_true", help="启动本地定时模式")
    parser.add_argument("--mode", choices=["morning", "evening"], default="morning")
    args = parser.parse_args()

    if args.schedule:
        run_scheduled()
    else:
        # 核心：将命令行解析出的 mode 传给执行函数
        push_once(mode=args.mode)
