"""
push.py - PushPlus 群组推送（完美复刻 Dribbble 莫兰迪风）
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
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") == 200:
            target = f"群组({PUSHPLUS_TOPIC})" if PUSHPLUS_TOPIC else "个人"
            print(f"  ✅ 推送成功！→ {target}")
            return True
        else:
            print(f"  ❌ 推送失败：{result.get('msg')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ 网络错误：{e}")
        return False


def build_html_content(
    date_str: str,
    mode: str,
    weather_sections: list,
    gemini_comment: str,
    gemini_news: str = "",
    love_msg: str = "",
    greeting: str = "",
) -> str:
    """构建 莫兰迪/清新风 HTML 推送消息"""

    # 1. 替换标题（已修改为中文）
    mode_label = "🌞 早安推送" if mode == "morning" else "🌙 晚安推送"
    mode_color = "#e17055" if mode == "morning" else "#6c5ce7"
    
    # 2. 精调莫兰迪配色（提取自原图）
    bg_color = "#E4EBE5"        # 莫兰迪低饱和背景绿
    card_bg = "#FFFFFF"         # 纯白卡片
    text_dark = "#1C3326"       # 深墨绿(标题)
    text_sub = "#73867A"        # 灰绿色(次要文字)
    accent_red = "#D65C4F"      # 砖红色(重点温度)
    yellow_card = "#FFF9EB"     # 奶油黄 AI 卡片

    if gemini_comment:
        gemini_comment = gemini_comment.replace("\n", "<br>")
    if gemini_news:
        gemini_news = gemini_news.replace("\n", "<br>")

    # 3. 天气区块（极简版，去掉了多余的单位 % 和 级，隐藏了空数据）
  weather_html = ""
    for w in weather_sections:
        weather_html += f"""
    <div style="background:{card_bg}; border-radius:20px; padding:20px; margin:16px 0; box-shadow:0 4px 14px rgba(0,0,0,0.02);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
            <p style="margin:0; font-size:18px; color:{text_dark}; font-weight:900;">
                {w['city']} <span style="font-size:14px; color:{text_sub}; font-weight:normal;">/ {w['person']}</span>
            </p>
            <p style="margin:0; font-size:20px; color:{accent_red}; font-weight:900;">
                {w['temp_min']}~{w['temp_max']}℃
            </p>
        </div>
        
        <div style="background:#F4F7F4; border-radius:12px; padding:12px; margin-bottom:12px; display:flex; align-items:center;">
            <span style="font-size:24px; margin-right:12px;">{w['emoji']}</span>
            <span style="color:{text_dark}; font-size:16px; font-weight:bold;">{w['text']} · 体感 {w.get('feels_like','--')}℃</span>
        </div>

        <div style="font-size:13px; color:{text_sub}; line-height:1.8;">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span>💧 湿度：<strong style="color:{text_dark};">{w.get('humidity','--')}%</strong></span>
                <span>☀️ 紫外线：<strong style="color:{text_dark};">{w.get('uv_index','--')}</strong></span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>🌅 日出：{w.get('sunrise','--')}</span>
                <span>🌇 日落：{w.get('sunset','--')}</span>
            </div>
        </div>
    </div>"""

    # ... 后面的组装逻辑保持不变 ...
    # (确保返回的 html 字符串包含这里的 weather_html)

    # Gemini 点评卡片
    comment_html = ""
    if gemini_comment:
        comment_html = f"""
    <div style="
        background: {yellow_card};
        border-radius: 20px;
        padding: 18px 20px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    ">
        <p style="margin:0 0 10px 0; font-size:14px; color:{accent_red}; font-weight:bold;">✨ AI 日常提醒</p>
        <p style="margin:0; font-size:14px; color:{text_dark}; line-height:1.8;">{gemini_comment}</p>
    </div>"""

    # 国际政治新闻卡片
    news_html = ""
    if gemini_news:
        news_html = f"""
    <div style="
        background: {card_bg};
        border-radius: 20px;
        padding: 18px 20px;
        margin: 16px 0;
        box-shadow: 0 4px 14px rgba(0,0,0,0.02);
    ">
        <p style="margin:0 0 12px 0; font-size:15px; color:{text_dark}; font-weight:bold;">🌍 每日国际视点</p>
        <p style="margin:0; font-size:14px; color:{text_sub}; line-height:1.8;">{gemini_news}</p>
    </div>"""

    # 主体组装 (新增了标题居中 text-align:center)
    html = f"""
<div style="
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    max-width: 480px;
    margin: 0 auto;
    padding: 24px 20px;
    background-color: {bg_color};
    border-radius: 30px;
">
    <div style="margin-bottom:24px; text-align:center;">
        <span style="
            display: inline-block;
            background: {card_bg};
            color: {text_sub};
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
            margin-bottom: 16px;
        ">📅 {date_str} ▾</span>
        
        <h2 style="color:{text_dark}; margin:0; font-size:28px; font-weight:900; letter-spacing:1px;">
            {mode_label}
        </h2>
        <p style="color:{text_sub}; font-size:15px; margin:8px 0 0 0;">
            {greeting}
        </p>
    </div>

    {weather_html}
    {comment_html}
    {news_html}

    <div style="
        background: {card_bg};
        border-radius: 20px;
        padding: 24px 20px;
        margin: 16px 0 30px 0;
        box-shadow: 0 4px 14px rgba(0,0,0,0.02);
        text-align: center;
    ">
        <span style="font-size:24px; display:block; margin-bottom:12px;">💌</span>
        <p style="margin:0; font-size:15px; color:{text_dark}; line-height:1.8; font-style:italic; font-weight:500;">
            "{love_msg}"
        </p>
    </div>
</div>
"""
    return html
