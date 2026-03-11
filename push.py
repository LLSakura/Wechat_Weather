"""
push.py - PushPlus 群组推送（莫兰迪 UI 优化版）
"""
import requests
from config import PUSHPLUS_TOKEN, PUSHPLUS_TOPIC

PUSHPLUS_URL = "http://www.pushplus.plus/send"

def send_message(title: str, content: str) -> bool:
    payload = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "html",
    }
    if PUSHPLUS_TOPIC:
        payload["topic"] = PUSHPLUS_TOPIC

    try:
        resp = requests.post(PUSHPLUS_URL, json=payload, timeout=15)
        result = resp.json()
        if result.get("code") == 200:
            print(f"  ✅ 推送成功！→ {'群组' if PUSHPLUS_TOPIC else '个人'}")
            return True
        print(f"  ❌ 推送失败：{result.get('msg')}")
    except Exception as e:
        print(f"  ❌ 推送异常：{e}")
    return False

def build_html_content(date_str, mode, weather_sections, gemini_comment, gemini_news="", love_msg="", greeting="") -> str:
    # 标题与配色
    mode_label = "🌞 早安推送" if mode == "morning" else "🌙 晚安推送"
    bg_color, card_bg, text_dark, text_sub, accent_red, yellow_card = (
        "#E4EBE5", "#FFFFFF", "#1C3326", "#73867A", "#D65C4F", "#FFF9EB"
    )

    # 预处理文本换行
    comment_fmt = gemini_comment.replace("\n", "<br>") if gemini_comment else ""
    news_fmt = gemini_news.replace("\n", "<br>") if gemini_news else ""

    # 1. 组装天气卡片
    weather_html = ""
    for w in weather_sections:
        weather_html += f"""
    <div style="background:{card_bg}; border-radius:20px; padding:20px; margin:16px 0; box-shadow:0 4px 14px rgba(0,0,0,0.02);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
            <p style="margin:0; font-size:18px; color:{text_dark}; font-weight:900;">
                {w['city']} <span style="font-size:14px; color:{text_sub}; font-weight:normal;">/ {w['person']}</span>
            </p>
            <p style="margin:0; font-size:20px; color:{accent_red}; font-weight:900;">{w['temp_min']}~{w['temp_max']}℃</p>
        </div>
        <div style="background:#F4F7F4; border-radius:12px; padding:12px; margin-bottom:12px; display:flex; align-items:center;">
            <span style="font-size:24px; margin-right:12px;">{w['emoji']}</span>
            <span style="color:{text_dark}; font-size:16px; font-weight:bold;">{w['text']} · 体感 {w.get('feels_like','--')}℃</span>
        </div>
        <div style="font-size:13px; color:{text_sub}; line-height:1.8;">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span>💧 湿度：<strong style="color:{text_dark};">{w.get('humidity','--')}</strong></span>
                <span>☀️ 紫外线：<strong style="color:{text_dark};">{w.get('uv_index','--')}</strong></span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>🌅 日出：{w.get('sunrise','--')}</span>
                <span>🌇 日落：{w.get('sunset','--')}</span>
            </div>
        </div>
    </div>"""

    # 2. AI 点评与新闻区块
    comment_html = f"""
    <div style="background:{yellow_card}; border-radius:20px; padding:18px 20px; margin:16px 0; box-shadow:0 4px 12px rgba(0,0,0,0.02);">
        <p style="margin:0 0 10px 0; font-size:14px; color:{accent_red}; font-weight:bold;">✨ AI 日常提醒</p>
        <p style="margin:0; font-size:14px; color:{text_dark}; line-height:1.8;">{comment_fmt}</p>
    </div>""" if gemini_comment else ""

    news_html = f"""
    <div style="background:{card_bg}; border-radius:20px; padding:18px 20px; margin:16px 0; box-shadow:0 4px 14px rgba(0,0,0,0.02);">
        <p style="margin:0 0 12px 0; font-size:15px; color:{text_dark}; font-weight:bold;">🌍 每日国际视点</p>
        <p style="margin:0; font-size:14px; color:{text_sub}; line-height:1.8;">{news_fmt}</p>
    </div>""" if gemini_news else ""

    # 3. 最终 HTML 组装
    return f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif; max-width:480px; margin:0 auto; padding:24px 20px; background-color:{bg_color}; border-radius:30px;">
    <div style="margin-bottom:24px; text-align:center;">
        <span style="display:inline-block; background:{card_bg}; color:{text_sub}; padding:6px 16px; border-radius:20px; font-size:13px; font-weight:600; box-shadow:0 2px 8px rgba(0,0,0,0.03); margin-bottom:16px;">📅 {date_str} ▾</span>
        <h2 style="color:{text_dark}; margin:0; font-size:28px; font-weight:900; letter-spacing:1px;">{mode_label}</h2>
        <p style="color:{text_sub}; font-size:15px; margin:8px 0 0 0;">{greeting}</p>
    </div>
    {weather_html}
    {comment_html}
    {news_html}
    <div style="background:{card_bg}; border-radius:20px; padding:24px 20px; margin:16px 0 30px 0; box-shadow:0 4px 14px rgba(0,0,0,0.02); text-align:center;">
        <span style="font-size:24px; display:block; margin-bottom:12px;">💌</span>
        <p style="margin:0; font-size:15px; color:{text_dark}; line-height:1.8; font-style:italic; font-weight:500;">"{love_msg}"</p>
    </div>
    <div style="text-align:center; margin-top:35px; padding:0 20px;">
        <p style="font-size:12px; color:{text_sub}; line-height:1.6; margin:0; letter-spacing:1px; opacity:0.8;">
            “在这漫长的一生里，你是那场永不落幕的晨光。”
        </p>
    </div>

    <p style="text-align:center; font-size:10px; color:#A0AFA6; margin-top:20px; opacity:0.5;">
        Design Inspired by Dribbble · AI Powered
    </p>
</div>
"""
