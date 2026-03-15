# from google import genai
from groq import Groq
import os

client = Groq(api_key=os.environ.get('GROQ_API_KEY', 'your-groq-key-here'))




MODEL  = 'llama-3.3-70b-versatile'



def ask_groq(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()


def generate_summary(content):
    try:
        return ask_groq(
            f"Summarize this blog  short sentences. "
            f"Return only the summary, nothing else.\n\n{content}"
        )
    except Exception as e:
        return f"Error: {str(e)}"


def generate_tags(title, content):
    try:
        return ask_groq(
            f"Generate 5 relevant comma separated tags.\n"
            f"Title: {title}\nContent: {content[:500]}\n"
            f"Return only tags like: python, django, web, api"
        )
    except Exception as e:
        return ""


def suggest_category(title, content):
    try:
        return ask_groq(
            f"Suggest ONE category from: Technology, Travel, Food, "
            f"Health, Education, Business, Sports, Entertainment, "
            f"Science, Lifestyle\n"
            f"Title: {title}\nContent: {content[:300]}\n"
            f"Return only category name."
        )
    except Exception as e:
        return "General"


def check_sentiment(comment_text):
    try:
        result = ask_groq(
            f"Return ONE word only (positive/negative/neutral/toxic):\n"
            f"{comment_text}"
        ).lower()
        if result not in ['positive', 'negative', 'neutral', 'toxic']:
            return 'neutral'
        return result
    except Exception as e:
        return 'neutral'


def chat_with_blog(question, post_titles):
    try:
        titles_text = "\n".join([f"- {t}" for t in post_titles])
        return ask_groq(
            f"You are a blog assistant.\n"
            f"Posts:\n{titles_text}\n\n"
            f"Question: {question}\n"
            f"Answer shortly and friendly."
        )
    except Exception as e:
        return "Sorry, I could not answer that right now."
