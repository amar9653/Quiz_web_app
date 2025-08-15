# Django Quiz Application Setup Guide

## Overview
This is a comprehensive Django-based quiz application with user authentication, customizable quizzes, detailed results, and an admin panel for question management.

## Features
- ✅ User Registration & Authentication
- ✅ Multiple Choice Questions with 4 Options
- ✅ Customizable Quiz Settings (difficulty, number of questions)
- ✅ Real-time Progress Tracking
- ✅ Detailed Results with Score Analysis
- ✅ User History and Statistics
- ✅ Leaderboard System
- ✅ Admin Panel for Question Management
- ✅ Responsive Design with Bootstrap 5
- ✅ SQLite Database (development)

## Requirements
- Python 3.8+
- Django 4.2+
- Modern web browser

## Installation Steps

### 1. Create Project Directory
```bash
mkdir django_quiz_app
cd django_quiz_app
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database
```bash
python manage.py makemigrations
python manage.py makemigrations quiz_app
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Load Sample Data (Optional)
```bash
python manage.py shell
```

Then in the Django shell:
```python
from quiz_app.models import QuizQuestion

# Sample questions
questions = [
    {
        'question_text': 'What is the capital of France?',
        'choice_a': 'London',
        'choice_b': 'Berlin',
        'choice_c': 'Paris',
        'choice_d': 'Madrid',
        'correct_answer': 'C',
        'difficulty_level': 'EASY'
    },
    {
        'question_text': 'Which programming language is Django built with?',
        'choice_a': 'JavaScript',
        'choice_b': 'Python',
        'choice_c': 'Java',
        'choice_d': 'PHP',
        'correct_answer': 'B',
        'difficulty_level': 'EASY'
    },
    {
        'question_text': 'What does CSS stand for?',
        'choice_a': 'Computer Style Sheets',
        'choice_b': 'Creative Style Sheets',
        'choice_c': 'Cascading Style Sheets',
        'choice_d': 'Colorful Style Sheets',
        'correct_answer': 'C',
        'difficulty_level': 'MEDIUM'
    },
    {
        'question_text': 'In which year was JavaScript created?',
        'choice_a': '1993',
        'choice_b': '1995',
        'choice_c': '1997',
        'choice_d': '1999',
        'correct_answer': 'B',
        'difficulty_level': 'HARD'
    }
]

for q_data in questions:
    QuizQuestion.objects.create(**q_data)

print("Sample questions created successfully!")
exit()
```

### 7. Run Development Server
```bash
python manage.py runserver
```

### 8. Access the Application
- Main Application: http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/

## Usage Guide

### For Users
1. Register a new account or login
2. Navigate to "Take Quiz" 
3. Configure quiz settings (number of questions, difficulty)
4. Answer all questions
5. Submit quiz and view detailed results
6. Check your history and compare with leaderboard

### For Administrators
1. Login to admin panel with superuser credentials
2. Navigate to "Quiz Questions" section
3. Add, edit, or delete questions
4. Use bulk actions to manage multiple questions
5. Monitor user scores in "User Scores" section

## Project Structure
```
quiz_project/
├── quiz_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── quiz_app/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── migrations/
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── quiz_setup.html
│   ├── quiz.html
│   ├── results.html
│   └── about.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── manage.py
└── requirements.txt
```

## Customization Options

### Adding New Question Fields
1. Modify the `QuizQuestion` model in `models.py`
2. Create and run migrations
3. Update admin interface and forms accordingly

### Styling Customization
- Modify `static/css/style.css` for visual changes
- Update templates for layout changes
- Customize Bootstrap themes

### Additional Features
- Email notifications
- Question categories
- Time limits per quiz
- Multimedia questions
- Export results to PDF

## Troubleshooting

### Common Issues
1. **Static files not loading**: Run `python manage.py collectstatic`
2. **Database errors**: Delete migrations and recreate them
3. **Permission errors**: Check user permissions and authentication
4. **Template not found**: Verify template paths in settings

### Database Reset
```bash
rm db.sqlite3
rm quiz_app/migrations/0*.py
python manage.py makemigrations quiz_app
python manage.py migrate
python manage.py createsuperuser
```

## Security Considerations
- Change `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Configure proper database for production
- Use HTTPS in production
- Implement rate limiting for quiz attempts

## Deployment
1. Use PostgreSQL or MySQL for production database
2. Configure static file serving (WhiteNoise or nginx)
3. Set environment variables for sensitive data
4. Use proper WSGI server (Gunicorn)
5. Configure reverse proxy (nginx)

## Support
For issues and questions:
1. Check Django documentation: https://docs.djangoproject.com/
2. Review code comments for implementation details
3. Test with sample data provided

## License
This project is open source and available under the MIT License.
