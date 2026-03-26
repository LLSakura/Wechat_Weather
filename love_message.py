"""
love_message.py - 使用 Gemini 生成：天气点评 + 国际政治新闻 + 个性化英语情话
"""
import random
import re  # ✨ 新增这行，引入正则库
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

**PART 2 - Hardcore Geopolitics & Tech News (in Chinese, 3 bullet points):**
You MUST act as a sharp, top-tier geopolitical and tech analyst. Provide 3 brief, highly specific bullet points covering recent MAJOR, world-shifting news. 

CRITICAL RULES:
- DO NOT output generic diplomatic summaries (e.g., "countries held a summit" or "signed a framework"). 
- Focus ONLY on high-impact events with concrete details (specific names of leaders, companies, or technologies).

Please structure the 3 points exactly as follows:
1. Superpower Dynamics: A major action by global superpowers (e.g., US Presidential decisions, US-China tech/trade policies, or significant geopolitical conflicts).
2. AI & Frontier Tech: A specific breakthrough, major release, or regulatory shift in Artificial Intelligence (e.g., updates on LLMs, OpenAI, tech giant moves, or new AI development frameworks).
3. Global Impact: A "wild-card" event that heavily influences global markets, energy, or supply chains.

Make the tone sharp, insightful, and straight to the point.

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
            },
        )
        text = response.text.strip()

        # ✨ --- 新的强壮解析逻辑开始 ---
        # 1. 过滤掉 AI 可能自动加上的 Markdown 加粗星号
        clean_text = text.replace("**", "")
        
        # 2. 使用正则表达式灵活提取（忽略大小写，且即使某一部分缺失也不会崩溃）
        comment_match = re.search(r'COMMENT:\s*(.*?)(?=NEWS:|LOVE:|$)', clean_text, re.DOTALL | re.IGNORECASE)
        news_match = re.search(r'NEWS:\s*(.*?)(?=LOVE:|$)', clean_text, re.DOTALL | re.IGNORECASE)
        love_match = re.search(r'LOVE:\s*(.*)', clean_text, re.DOTALL | re.IGNORECASE)
        
        comment = comment_match.group(1).strip() if comment_match else ""
        news = news_match.group(1).strip() if news_match else ""
        love = love_match.group(1).strip().strip('"').strip("'") if love_match else ""
        
        # 3. 极端兜底：如果完全没有按格式输出，把整个文本扔给 love
        if not comment_match and not news_match and not love_match:
            love = clean_text.strip('"').strip("'").strip()
        # ✨ --- 新的强壮解析逻辑结束 ---

        return {
            "comment": comment if comment else "",
            "news": news if news else "今日国际新闻生成失败（AI可能无法获取最新资讯）。",
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
