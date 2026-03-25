"""
love_message.py - 使用 Gemini 生成：天气点评 + 国际政治新闻 + 个性化英语情话
"""
import random
from datetime import datetime

from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

CLASSIC_LOVE_MESSAGES = [
    "You are my today and all of my tomorrows.",
    "In a sea of people, my eyes will always search for you.",
    "Every love story is beautiful, but ours is my favorite.",
    "I fell in love the way you fall asleep: slowly, and then all at once.",
    "You are my sun, my moon, and all my stars.",
    "If I had a flower for every time I thought of you, I could walk through my garden forever.",
    "My heart is and always will be yours.",
    "You are my greatest adventure.",
    "I love you to the moon and back.",
    "Wherever you are is my home.",
    "I choose you. And I'll choose you over and over.",
    "If I know what love is, it is because of you.",
    "You are the poem I never knew how to write.",
    "I'd choose you in a hundred lifetimes, in any version of reality.",
    "My favorite place in the world is next to you.",
    "I love you more than yesterday, less than tomorrow.",
]


def generate_love_message(
    weather_sections: list,
    mode: str = "morning",
    date_str: str = "",
) -> dict:
    """
    使用 Gemini 生成：天气点评 + 国际政治新闻 + 英语情话

    Returns:
        dict: {"comment": "天气点评...", "news": "国际政治...", "love": "英语情话..."}
    """
    if not GEMINI_API_KEY:
        return {
            "comment": "",
            "news": "暂无新闻（未配置 API Key）",
            "love": random.choice(CLASSIC_LOVE_MESSAGES),
        }

    time_label = "早上 (morning)" if mode == "morning" else "晚上 (evening)"
    weather_desc = "\n".join(
        f"- {w['person']} 在 {w['city']}：{w['text']} {w.get('temp_min','--')}~{w.get('temp_max','--')}℃, "
        f"体感{w.get('feels_like','--')}℃, 湿度{w.get('humidity','--')}%, "
        f"风{w.get('wind_dir','--')}{w.get('wind_scale','--')}级"
        for w in weather_sections
    )
    
    # 动态提取要发送的人名（自动获取你配置的 Sakura 和 之间）
    people_names = " and ".join([w['person'] for w in weather_sections])

    inspirations = random.sample(CLASSIC_LOVE_MESSAGES, 3)
    inspiration_text = "\n".join(f"  - {m}" for m in inspirations)

    prompt = f"""You are writing a daily message for: {people_names}.

Today's info:
- Date: {date_str or datetime.now().strftime('%Y-%m-%d')}
- Time of day: {time_label}
- Weather:
{weather_desc}

Please write THREE parts, clearly labeled:

**PART 1 - Weather Commentary (in Chinese, 2-3 sentences):**
Based on the weather above, give a warm, caring comment. Be specific to the actual weather data. Address them by name.

**PART 2 - Real-Time International Politics (in Chinese, 3 bullet points):**
You MUST act as a strict real-time news aggregator. Provide 3 brief, objective bullet points covering the MOST IMPORTANT global international political news that happened STRICTLY within the past 24 hours (Leading up to today: {date_str or datetime.now().strftime('%Y-%m-%d')}). 

Focus specifically on:
- Meetings between heads of state (e.g., bilateral talks, summits).
- Major diplomatic statements or policy shifts.
- Crucial geopolitical events.

CRITICAL: Do NOT output old news. If no major political news happened in the last 24 hours, provide the most recent significant geopolitical updates.

**PART 3 - Love Message (in English, 2-3 sentences):**
Write a sweet, poetic English love message. Naturally weave in the weather or time of day. Make it feel personal to {people_names}.

Style inspirations for Part 3 (do NOT copy these):
{inspiration_text}

Format your response EXACTLY like this (keep the labels):
COMMENT: [your Chinese weather commentary here]
NEWS: [your 3 bullet points of international news here]
LOVE: [your English love message here]"""

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "temperature": 0.4, # 📉 调低温度，让新闻更严谨客观，减少幻觉
                "max_output_tokens": 1024,
                "tools": [{"google_search": {}}], # 🌐 核心魔法：开启谷歌联网搜索！
            },
        )
        text = response.text.strip()


        # 解析 COMMENT, NEWS 和 LOVE
        comment = ""
        news = ""
        love = ""
        
        if "COMMENT:" in text and "NEWS:" in text and "LOVE:" in text:
            try:
                parts = text.split("NEWS:")
                comment = parts[0].replace("COMMENT:", "").strip()
                
                parts2 = parts[1].split("LOVE:")
                news = parts2[0].strip()
                love = parts2[1].strip().strip('"').strip("'").strip()
            except Exception:
                love = text.strip('"').strip("'").strip()
        else:
            # 如果格式不对，整段作为 love 兜底
            love = text.strip('"').strip("'").strip()

        return {
            "comment": comment if comment else "",
            "news": news if news else "今日国际新闻生成失败。",
            "love": love if love else random.choice(CLASSIC_LOVE_MESSAGES),
        }
    except Exception as e:
        print(f"  ⚠️ Gemini 调用失败（{e}），使用经典情话")
        return {
            "comment": "",
            "news": "API 调用失败，暂无新闻",
            "love": random.choice(CLASSIC_LOVE_MESSAGES),
        }


if __name__ == "__main__":
    test_sections = [
        {"person": "Sakura", "city": "北京", "text": "晴", "temp_min": "2", "temp_max": "16",
         "feels_like": "10", "humidity": "14", "wind_dir": "东北风", "wind_scale": "2"},
        {"person": "之间", "city": "南康", "text": "晴", "temp_min": "9", "temp_max": "21",
         "feels_like": "15", "humidity": "50", "wind_dir": "东北风", "wind_scale": "1"},
    ]
    result = generate_love_message(test_sections, mode="morning")
    print(f"📝 点评：\n{result['comment']}\n")
    print(f"🌍 新闻：\n{result['news']}\n")
    print(f"💕 情话：\n{result['love']}")
