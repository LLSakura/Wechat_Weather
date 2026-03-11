"""
push.py - PushPlus 群组推送（莫兰迪清新风 UI + 国际新闻 + 情话）
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
    gemini_news: str = "",  # 新增的国际政治新闻参数
    love_msg: str = "",
    greeting: str = "",
) -> str:
    """构建 莫兰迪/清新风 HTML 推送消息"""

    mode_label = "Morning Push" if mode == "morning" else "Evening Push"
    
    # 颜色定义 (复刻图中的配色)
    bg_color = "#E6EFE9"        # 鼠尾草绿背景
    card_bg = "#FFFFFF"         # 纯白卡片
    text_dark = "#2D3A33"       # 深绿色字体(标题)
    text_sub = "#6E8074"        # 灰绿色字体(正文)
    accent_red = "#D86B5A"      # 砖红色点缀 (复刻 $2.5k 的颜色)
    yellow_card = "#FDF8E1"     # 淡黄色高亮卡片 (给点评和情话)

    # 替换换行符，以便在 HTML 中正确显示 Gemini 的格式
    if gemini_comment:
        gemini_comment = gemini_comment.replace("\n", "<br>")
    if gemini_news:
        gemini_news = gemini_news.replace("\n", "<br>")

    # 天气区块（清新卡片版）
    weather_html = ""
    for w in weather_sections:
        weather_html += f"""
    <div style="
        background: {card_bg};
        border-radius: 20px;
        padding: 18px 20px;
        margin: 16px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.03);
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <p style="margin:0; font-size:18px; color:{text_dark}; font-weight:bold;">
                {w['city']} <span style="font-size:14px; color:{text_sub}; font-weight:normal;">/ {w['person']}</span>
            </p>
            <p style="margin:0; font-size:18px; color:{accent_red}; font-weight:bold;">
                {w['temp_min']}~{w['temp_max']}℃
            </p>
        </div>
        
        <div style="background:#F4F6F0; border-radius:12px; padding:10px; margin-bottom:10px; display:flex; align-items:center;">
            <span style="font-size:24px; margin-right:10px;">{w['emoji']}</span>
            <span style="color:{text_dark}; font-size:15px; font-weight:bold;">{w['text']}</span>
            <span style="color:{text_sub}; font-size:13px; margin-left:auto;">体感 {w.get('feels_like','--')}℃</span>
        </div>

        <p style="margin:4px 0; font-size:13px; color:{text_sub}; line-height:1.6;">
            💧 湿度：<strong style="color:{text_dark};">{w.get('humidity','--')}%</strong> &nbsp;&nbsp; 
            💨 风向：<strong style="color:{text_dark};">{w.get('wind_dir','--')}{w.get('wind_scale','--')}级</strong><br>
            🌅 日出：{w.get('sunrise','--')} &nbsp;&nbsp; 🌇 日落：{w.get('sunset','--')}
        </p>
    </div>"""

    # Gemini 点评卡片
    comment_html = ""
    if gemini_comment:
        comment_html = f"""
    <div style="
        background: {yellow_card};
        border-radius: 20px;
        padding: 16px 20px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    ">
        <p style="margin:0 0 8px 0; font-size:14px; color:{accent_red}; font-weight:bold;">✨ AI 日常提醒</p>
        <p style="margin:0; font-size:14px; color:{text_dark}; line-height:1.7;">{gemini_comment}</p>
    </div>"""

    # 新增：国际政治新闻卡片
    news_html = ""
    if gemini_news:
        news_html = f"""
    <div style="
        background: {card_bg};
        border-radius: 20px;
        padding: 18px 20px;
        margin: 16px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.03);
    ">
        <p style="margin:0 0 12px 0; font-size:16px; color:{text_dark}; font-weight:bold;">🌍 每日国际视点</p>
        <p style="margin:0; font-size:14px; color:{text_sub}; line-height:1.8;">{gemini_news}</p>
    </div>"""

    # 主体组装
    html = f"""
<div style="
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    max-width: 480px;
    margin: 0 auto;
    padding: 24px 20px;
    background-color: {bg_color};
    border-radius: 30px;
">
    <div style="margin-bottom:20px;">
        <span style="
            display: inline-block;
            background: {card_bg};
            color: {text_sub};
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
            margin-bottom: 12px;
        ">📅 {date_str} ▾</span>
        
        <h2 style="color:{text_dark}; margin:0; font-size:26px; font-weight:800; letter-spacing:0.5px;">
            {mode_label}
        </h2>
        <p style="color:{text_sub}; font-size:14px; margin:4px 0 0 0;">
            {greeting}
        </p>
    </div>

    {weather_html}

    {comment_html}

    {news_html}

    <div style="
        background: {card_bg};
        border-radius: 20px;
        padding: 20px;
        margin: 16px 0 30px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.03);
        text-align: center;
    ">
        <span style="font-size:24px; display:block; margin-bottom:10px;">💌</span>
        <p style="margin:0; font-size:15px; color:{text_dark}; line-height:1.8; font-style:italic; font-weight:500;">
            "{love_msg}"
        </p>
    </div>

    <p style="text-align:center; font-size:12px; color:#A0AFA6; margin:0;">
        Design Inspired by Dribbble · AI Powered
    </p>
</div>
"""
    return html
