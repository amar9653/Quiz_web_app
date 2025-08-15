from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count, Avg
from django.utils.html import format_html
from .models import QuizQuestion, UserScore


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """Admin interface for QuizQuestion model"""

    list_display = (
        'id',
        'question_preview',
        'difficulty_level',
        'correct_answer',
        'is_active',
        'created_at',
        'question_stats'
    )

    list_filter = (
        'difficulty_level',
        'correct_answer',
        'is_active',
        'created_at',
    )

    search_fields = (
        'question_text',
        'choice_a',
        'choice_b', 
        'choice_c',
        'choice_d'
    )

    list_editable = ('is_active', 'difficulty_level')

    ordering = ('-created_at',)

    fieldsets = (
        ('Question Information', {
            'fields': ('question_text', 'difficulty_level', 'is_active')
        }),
        ('Multiple Choice Options', {
            'fields': ('choice_a', 'choice_b', 'choice_c', 'choice_d')
        }),
        ('Correct Answer', {
            'fields': ('correct_answer',),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        })
    )

    readonly_fields = ('created_at', 'updated_at')

    actions = ['activate_questions', 'deactivate_questions', 'duplicate_questions']

    def question_preview(self, obj):
        """Show a preview of the question text"""
        preview = obj.question_text[:100]
        if len(obj.question_text) > 100:
            preview += "..."
        return preview
    question_preview.short_description = "Question Preview"

    def question_stats(self, obj):
        """Show statistics for this question"""
        # Count how many times this question was answered
        total_attempts = UserScore.objects.filter(
            quiz_questions__contains=[{'id': obj.id}]
        ).count()

        if total_attempts > 0:
            return format_html(
                '<span style="color: green;">Used {}</span> times',
                total_attempts
            )
        else:
            return format_html('<span style="color: orange;">Not used yet</span>')
    question_stats.short_description = "Usage Stats"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related()

    def activate_questions(self, request, queryset):
        """Bulk action to activate selected questions"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} questions were successfully activated.'
        )
    activate_questions.short_description = "Activate selected questions"

    def deactivate_questions(self, request, queryset):
        """Bulk action to deactivate selected questions"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} questions were successfully deactivated.'
        )
    deactivate_questions.short_description = "Deactivate selected questions"

    def duplicate_questions(self, request, queryset):
        """Bulk action to duplicate selected questions"""
        duplicated = 0
        for question in queryset:
            question.pk = None  # This will create a new object when saved
            question.question_text = f"[COPY] {question.question_text}"
            question.is_active = False  # Deactivate copies by default
            question.save()
            duplicated += 1

        self.message_user(
            request,
            f'{duplicated} questions were successfully duplicated (marked as inactive).'
        )
    duplicate_questions.short_description = "Duplicate selected questions"


@admin.register(UserScore)
class UserScoreAdmin(admin.ModelAdmin):
    """Admin interface for UserScore model"""

    list_display = (
        'id',
        'user',
        'score_display',
        'percentage_display', 
        'grade_display',
        'time_taken_display',
        'completed_at'
    )

    list_filter = (
        'completed_at',
        'total_questions',
        'percentage',
    )

    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name'
    )

    ordering = ('-completed_at',)

    readonly_fields = (
        'user',
        'score',
        'total_questions', 
        'percentage',
        'time_taken',
        'completed_at',
        'user_answers_display',
        'quiz_questions_display'
    )

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'completed_at')
        }),
        ('Score Information', {
            'fields': ('score', 'total_questions', 'percentage', 'time_taken')
        }),
        ('Detailed Results', {
            'fields': ('user_answers_display', 'quiz_questions_display'),
            'classes': ('collapse',)
        })
    )

    def score_display(self, obj):
        """Display score as fraction"""
        return f"{obj.score}/{obj.total_questions}"
    score_display.short_description = "Score"

    def percentage_display(self, obj):
        """Display percentage with color coding"""
        color = "green" if obj.percentage >= 80 else "orange" if obj.percentage >= 60 else "red"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, obj.percentage
        )
    percentage_display.short_description = "Percentage"

    def grade_display(self, obj):
        """Display letter grade with color"""
        grade = obj.get_grade()
        color = {
            'A': 'green',
            'B': 'blue', 
            'C': 'orange',
            'D': 'orange',
            'F': 'red'
        }.get(grade, 'black')

        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 16px;">{}</span>',
            color, grade
        )
    grade_display.short_description = "Grade"

    def time_taken_display(self, obj):
        """Display time taken in a readable format"""
        if obj.time_taken:
            total_seconds = int(obj.time_taken.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        return "Not recorded"
    time_taken_display.short_description = "Time Taken"

    def user_answers_display(self, obj):
        """Display user answers in a readable format"""
        if obj.user_answers:
            answers_html = "<ul>"
            for question_id, answer in obj.user_answers.items():
                answers_html += f"<li>Question {question_id}: <strong>{answer}</strong></li>"
            answers_html += "</ul>"
            return format_html(answers_html)
        return "No answers recorded"
    user_answers_display.short_description = "User Answers"

    def quiz_questions_display(self, obj):
        """Display quiz questions in a readable format"""
        if obj.quiz_questions:
            questions_html = "<ol>"
            for q in obj.quiz_questions:
                correct_choice = q.get('choices', {}).get(q.get('correct_answer', ''), 'Unknown')
                questions_html += f"""
                <li style="margin-bottom: 10px;">
                    <strong>{q.get('question', 'No question text')}</strong><br>
                    <small>Correct Answer: {q.get('correct_answer', '?')} - {correct_choice}</small>
                </li>
                """
            questions_html += "</ol>"
            return format_html(questions_html)
        return "No questions recorded"
    quiz_questions_display.short_description = "Quiz Questions"

    def has_add_permission(self, request):
        """Disable adding new scores through admin"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing scores through admin"""
        return False


# Customize the admin site header and title
admin.site.site_header = "Quiz Application Admin"
admin.site.site_title = "Quiz Admin"
admin.site.index_title = "Welcome to Quiz Application Administration"

# Add some custom styling
admin.site.enable_nav_sidebar = True