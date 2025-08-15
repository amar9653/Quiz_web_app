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

