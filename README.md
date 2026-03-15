# DjangoBlog

A full-stack blog website built with Django + REST API + AI features.

## Tech Stack
- Python 3.9
- Django 4.2
- Django REST Framework
- PostgreSQL
- Groq AI (Llama 3.3)
- Bootstrap 5
- JWT Authentication

## Features
- Blog posts with CRUD
- REST API with JWT auth
- AI post summarization
- AI comment sentiment analysis
- AI chatbot
- Search and pagination
- Admin panel

## Setup

1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install packages: `pip install -r requirements.txt`
5. Add your keys in `ai_helper.py` and `settings.py`
6. Run migrations: `python manage.py migrate`
7. Run server: `python manage.py runserver`

## API Endpoints
- `GET /api/posts/` - List all posts
- `POST /api/posts/` - Create post
- `POST /api/jwt/login/` - Login
- `POST /api/jwt/register/` - Register
- `POST /api/ai/summarize/` - AI summary
