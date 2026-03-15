from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.environ.get('GROQ_API_KEY', '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'))
# client = Groq(api_key='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')



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
            f"Summarize this blog post in exactly 3 short sentences. "
            f"Return only the summary.\n\n{content}"
        )
    except Exception as e:
        return f"Error: {str(e)}"


def generate_tags(title, content):
    try:
        return ask_groq(
            f"Generate 5 comma separated tags.\n"
            f"Title: {title}\nContent: {content[:500]}\n"
            f"Return only tags."
        )
    except Exception as e:
        return ""


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


def chat_with_blog(question, post_data):
    try:
        # post_data is a list of dicts with title and content
        if len(post_data) == 1:
            # Single post page — use full content
            context = f"Title: {post_data[0]['title']}\n\nContent: {post_data[0]['content']}"
            prompt  = (
                f"You are a helpful assistant for this specific blog post.\n\n"
                f"Post:\n{context}\n\n"
                f"User question: {question}\n\n"
                f"Answer based only on this post content. Be short and friendly."
            )
        else:
            # Home page — use all post titles and short snippets
            context = "\n".join([
                f"- {p['title']}: {p['content'][:100]}..."
                for p in post_data
            ])
            prompt  = (
                f"You are a helpful assistant for a blog website.\n\n"
                f"Available posts:\n{context}\n\n"
                f"User question: {question}\n\n"
                f"Answer based on all available posts. Be short and friendly."
            )
        return ask_groq(prompt)
    except Exception as e:
        return "Sorry, I could not answer that right now."