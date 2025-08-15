from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

class QuizQuestion(models.Model):
    """Model for quiz questions with multiple choice answers"""

    question_text = models.TextField(
        help_text="Enter the quiz question",
        validators=[MinLengthValidator(10, "Question must be at least 10 characters long")]
    )

    choice_a = models.CharField(
        max_length=200,
        help_text="First choice option",
        validators=[MinLengthValidator(1, "Choice cannot be empty")]
    )

    choice_b = models.CharField(
        max_length=200,
        help_text="Second choice option",
        validators=[MinLengthValidator(1, "Choice cannot be empty")]
    )

    choice_c = models.CharField(
        max_length=200,
        help_text="Third choice option",
        validators=[MinLengthValidator(1, "Choice cannot be empty")]
    )

    choice_d = models.CharField(
        max_length=200,
        help_text="Fourth choice option",
        validators=[MinLengthValidator(1, "Choice cannot be empty")]
    )

    ANSWER_CHOICES = [
        ('A', 'Choice A'),
        ('B', 'Choice B'),
        ('C', 'Choice C'),
        ('D', 'Choice D'),
    ]

    correct_answer = models.CharField(
        max_length=1,
        choices=ANSWER_CHOICES,
        help_text="Select the correct answer"
    )

    difficulty_level = models.CharField(
        max_length=10,
        choices=[
            ('EASY', 'Easy'),
            ('MEDIUM', 'Medium'),
            ('HARD', 'Hard'),
        ],
        default='MEDIUM',
        help_text="Difficulty level of the question"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Is this question active in quizzes?")

    class Meta:
        verbose_name = "Quiz Question"
        verbose_name_plural = "Quiz Questions"
        ordering = ['-created_at']

    def __str__(self):
        return f"Q{self.id}: {self.question_text[:50]}..."

    def get_choices(self):
        """Return a list of all choices"""
        return [
            ('A', self.choice_a),
            ('B', self.choice_b),
            ('C', self.choice_c),
            ('D', self.choice_d),
        ]

    def get_correct_choice_text(self):
        """Return the text of the correct answer"""
        choices_map = {
            'A': self.choice_a,
            'B': self.choice_b,
            'C': self.choice_c,
            'D': self.choice_d,
        }
        return choices_map.get(self.correct_answer, '')


class UserScore(models.Model):
    """Model to track user quiz scores"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_scores',
        help_text="User who took the quiz"
    )

    score = models.IntegerField(
        help_text="Number of correct answers"
    )

    total_questions = models.IntegerField(
        help_text="Total number of questions in the quiz"
    )

    percentage = models.FloatField(
        help_text="Percentage score calculated automatically"
    )

    time_taken = models.DurationField(
        null=True, 
        blank=True,
        help_text="Time taken to complete the quiz"
    )

    completed_at = models.DateTimeField(auto_now_add=True)

    # Store user answers for detailed results
    user_answers = models.JSONField(
        default=dict,
        help_text="JSON field storing user's answers with question IDs"
    )

    quiz_questions = models.JSONField(
        default=list,
        help_text="JSON field storing the questions that were in this quiz attempt"
    )

    class Meta:
        verbose_name = "User Score"
        verbose_name_plural = "User Scores"
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.score}/{self.total_questions} ({self.percentage:.1f}%)"

    def save(self, *args, **kwargs):
        """Calculate percentage before saving"""
        if self.total_questions > 0:
            self.percentage = (self.score / self.total_questions) * 100
        else:
            self.percentage = 0.0
        super().save(*args, **kwargs)

    def get_grade(self):
        """Return letter grade based on percentage"""
        if self.percentage >= 90:
            return 'A'
        elif self.percentage >= 80:
            return 'B'
        elif self.percentage >= 70:
            return 'C'
        elif self.percentage >= 60:
            return 'D'
        else:
            return 'F'

    def is_passed(self):
        """Return True if user passed (60% or above)"""
        return self.percentage >= 60