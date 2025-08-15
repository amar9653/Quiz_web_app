from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Q, Avg, Count
from datetime import datetime, timedelta
import json
import random

from .models import QuizQuestion, UserScore
from .forms import CustomUserCreationForm, QuizForm, QuizSettingsForm


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get some statistics for the home page
        context['total_questions'] = QuizQuestion.objects.filter(is_active=True).count()

        if self.request.user.is_authenticated:
            user_scores = UserScore.objects.filter(user=self.request.user)
            context['user_attempts'] = user_scores.count()

            if user_scores.exists():
                context['best_score'] = user_scores.order_by('-percentage').first()
                context['average_score'] = user_scores.aggregate(avg=Avg('percentage'))['avg']
                context['recent_scores'] = user_scores.order_by('-completed_at')[:5]

        return context


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


class CustomLoginView(LoginView):
    """Custom login view"""
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        messages.success(self.request, f'Welcome back, {self.request.user.username}!')
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


@login_required
def quiz_setup_view(request):
    """Quiz setup page where users can configure quiz settings"""
    if request.method == 'POST':
        form = QuizSettingsForm(request.POST)
        if form.is_valid():
            # Store quiz settings in session
            request.session['quiz_settings'] = {
                'num_questions': form.cleaned_data['num_questions'],
                'difficulty': form.cleaned_data['difficulty'],
                'random_order': form.cleaned_data['random_order'],
            }
            return redirect('quiz')
    else:
        form = QuizSettingsForm()

    total_questions = QuizQuestion.objects.filter(is_active=True).count()

    return render(request, 'quiz_setup.html', {
        'form': form,
        'total_questions': total_questions
    })


@login_required
def quiz_view(request):
    """Main quiz view"""

    # Get quiz settings from session or use defaults
    quiz_settings = request.session.get('quiz_settings', {
        'num_questions': 10,
        'difficulty': 'ALL',
        'random_order': True
    })

    # Build query for questions
    questions_query = QuizQuestion.objects.filter(is_active=True)

    if quiz_settings['difficulty'] != 'ALL':
        questions_query = questions_query.filter(difficulty_level=quiz_settings['difficulty'])

    # Get questions
    if quiz_settings['random_order']:
        questions = list(questions_query.order_by('?')[:quiz_settings['num_questions']])
    else:
        questions = list(questions_query[:quiz_settings['num_questions']])

    if not questions:
        messages.error(request, 'No questions available for the selected criteria.')
        return redirect('quiz_setup')

    if request.method == 'POST':
        form = QuizForm(request.POST, questions=questions)
        if form.is_valid():
            # Store start time if not already stored
            if 'quiz_start_time' not in request.session:
                request.session['quiz_start_time'] = timezone.now().isoformat()

            # Calculate score
            user_answers = form.get_user_answers()
            score = 0
            correct_answers = {}

            for question in questions:
                correct_answers[question.id] = question.correct_answer
                if user_answers.get(question.id) == question.correct_answer:
                    score += 1

            # Calculate time taken
            start_time_str = request.session.get('quiz_start_time')
            if start_time_str:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                time_taken = timezone.now() - start_time.replace(tzinfo=timezone.utc)
            else:
                time_taken = None

            # Save score to database
            user_score = UserScore.objects.create(
                user=request.user,
                score=score,
                total_questions=len(questions),
                time_taken=time_taken,
                user_answers=user_answers,
                quiz_questions=[{
                    'id': q.id,
                    'question': q.question_text,
                    'choices': dict(q.get_choices()),
                    'correct_answer': q.correct_answer
                } for q in questions]
            )

            # Store result in session and redirect to results
            request.session['quiz_result_id'] = user_score.id

            # Clear quiz session data
            if 'quiz_start_time' in request.session:
                del request.session['quiz_start_time']
            if 'quiz_settings' in request.session:
                del request.session['quiz_settings']

            return redirect('quiz_results')
    else:
        # Store start time when quiz loads
        request.session['quiz_start_time'] = timezone.now().isoformat()
        form = QuizForm(questions=questions)

    context = {
        'form': form,
        'questions': questions,
        'question_count': len(questions),
        'quiz_settings': quiz_settings
    }

    return render(request, 'quiz.html', context)


@login_required 
def quiz_results_view(request):
    """Quiz results view"""
    result_id = request.session.get('quiz_result_id')

    if not result_id:
        messages.error(request, 'No quiz results found. Please take a quiz first.')
        return redirect('home')

    user_score = get_object_or_404(UserScore, id=result_id, user=request.user)

    # Prepare detailed results
    detailed_results = []
    for question_data in user_score.quiz_questions:
        question_id = question_data['id']
        user_answer = user_score.user_answers.get(str(question_id), 'Not answered')
        correct_answer = question_data['correct_answer']

        detailed_results.append({
            'question': question_data['question'],
            'choices': question_data['choices'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': user_answer == correct_answer,
            'correct_text': question_data['choices'].get(correct_answer, 'Unknown'),
            'user_text': question_data['choices'].get(user_answer, 'Not answered')
        })

    context = {
        'user_score': user_score,
        'detailed_results': detailed_results,
        'percentage': round(user_score.percentage, 1),
        'grade': user_score.get_grade(),
        'passed': user_score.is_passed()
    }

    # Clear the result from session after displaying
    if 'quiz_result_id' in request.session:
        del request.session['quiz_result_id']

    return render(request, 'results.html', context)


@login_required
def user_history_view(request):
    """View user's quiz history"""
    user_scores = UserScore.objects.filter(user=request.user).order_by('-completed_at')

    # Calculate statistics
    total_attempts = user_scores.count()
    if total_attempts > 0:
        best_score = user_scores.order_by('-percentage').first()
        average_score = user_scores.aggregate(avg=Avg('percentage'))['avg']
        total_questions_answered = sum(score.total_questions for score in user_scores)
        total_correct_answers = sum(score.score for score in user_scores)
    else:
        best_score = None
        average_score = 0
        total_questions_answered = 0
        total_correct_answers = 0

    context = {
        'user_scores': user_scores,
        'total_attempts': total_attempts,
        'best_score': best_score,
        'average_score': round(average_score, 1) if average_score else 0,
        'total_questions_answered': total_questions_answered,
        'total_correct_answers': total_correct_answers,
        'overall_accuracy': round((total_correct_answers / total_questions_answered * 100), 1) if total_questions_answered > 0 else 0
    }

    return render(request, 'user_history.html', context)


@login_required
def leaderboard_view(request):
    """Leaderboard showing top performers"""
    # Get top scores (best attempt per user)
    from django.db.models import Max

    top_scores = UserScore.objects.values('user__username', 'user__first_name', 'user__last_name').annotate(
        best_score=Max('percentage'),
        total_attempts=Count('id'),
        avg_score=Avg('percentage')
    ).order_by('-best_score')[:20]

    # Recent high scores
    recent_high_scores = UserScore.objects.filter(
        percentage__gte=80
    ).select_related('user').order_by('-completed_at')[:10]

    context = {
        'top_scores': top_scores,
        'recent_high_scores': recent_high_scores
    }

    return render(request, 'leaderboard.html', context)


def about_view(request):
    """About page"""
    return render(request, 'about.html')