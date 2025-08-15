from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import QuizQuestion

class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form with additional fields"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        }),
        help_text="We'll never share your email with anyone else."
    )

    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name (optional)'
        })
    )

    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name (optional)'
        })
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class QuizForm(forms.Form):
    """Dynamic form for quiz questions"""

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions', [])
        super().__init__(*args, **kwargs)

        for question in questions:
            # Create a radio button field for each question
            choices = [
                ('A', question.choice_a),
                ('B', question.choice_b), 
                ('C', question.choice_c),
                ('D', question.choice_d),
            ]

            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.question_text,
                choices=choices,
                widget=forms.RadioSelect(attrs={
                    'class': 'form-check-input'
                }),
                required=True,
                error_messages={'required': 'Please select an answer for this question.'}
            )

    def get_user_answers(self):
        """Extract user answers from cleaned data"""
        answers = {}
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('question_'):
                question_id = int(field_name.replace('question_', ''))
                answers[question_id] = value
        return answers


class QuizSettingsForm(forms.Form):
    """Form for quiz settings (number of questions, difficulty, etc.)"""

    DIFFICULTY_CHOICES = [
        ('ALL', 'All Difficulties'),
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'), 
        ('HARD', 'Hard'),
    ]

    num_questions = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=10,
        label="Number of Questions",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '10'
        }),
        help_text="Choose between 1 and 50 questions"
    )

    difficulty = forms.ChoiceField(
        choices=DIFFICULTY_CHOICES,
        initial='ALL',
        label="Difficulty Level",
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="Filter questions by difficulty level"
    )

    random_order = forms.BooleanField(
        required=False,
        initial=True,
        label="Random Question Order",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Randomize the order of questions"
    )

    def clean_num_questions(self):
        num_questions = self.cleaned_data['num_questions']

        # Check if there are enough questions in the database
        total_available = QuizQuestion.objects.filter(is_active=True).count()

        if num_questions > total_available:
            raise forms.ValidationError(
                f"Only {total_available} questions are available. "
                f"Please choose a smaller number."
            )

        return num_questions


class ContactForm(forms.Form):
    """Contact form for user feedback"""

    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter subject'
        })
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter your message'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address'
        })
    )