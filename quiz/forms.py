from django import forms
from .models import Quiz, Question, Answer
from datetime import timedelta


class QuizCreateForm(forms.ModelForm):
    # Accept time limit as a HH:MM string from the user (hours:minutes)
    time_limit = forms.CharField(
        required=False,
        label='Час (години:хвилини)',
        help_text='Введіть у форматі "години:хвилини", наприклад 0:30 або 1:15'
    )

    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit', 'code']

    def clean_time_limit(self):
        raw = self.cleaned_data.get('time_limit')
        if not raw:
            return None

        # Allow inputs like 'H:M' or 'HH:MM' or 'MM' (treated as minutes)
        raw = raw.strip()
        try:
            if ':' in raw:
                parts = raw.split(':')
                if len(parts) != 2:
                    raise ValueError('Неправильний формат часу')
                hours = int(parts[0])
                minutes = int(parts[1])
            else:
                # only minutes provided
                hours = 0
                minutes = int(raw)
        except Exception:
            raise forms.ValidationError('Час має бути у форматі годин:хвилин, напр. 1:30')

        if hours < 0 or minutes < 0 or minutes >= 60:
            raise forms.ValidationError('Неправильні значення годин або хвилин')

        return timedelta(hours=hours, minutes=minutes)

    def save(self, commit=True):
        # The cleaned time_limit is a timedelta or None and matches the model field
        instance = super().save(commit=False)
        instance.time_limit = self.cleaned_data.get('time_limit')
        # ensure code is set (if user left it blank, generate one)
        if not instance.code:
            # generate a short alphanumeric code
            import secrets, string
            alphabet = string.ascii_uppercase + string.digits
            for _ in range(10):
                candidate = ''.join(secrets.choice(alphabet) for _ in range(6))
                if not Quiz.objects.filter(code=candidate).exists():
                    instance.code = candidate
                    break
        if commit:
            instance.save()
        return instance


# Simple Question form for creation step (single question minimum)
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', 'order', 'image')

    def clean_image(self):
        img = self.cleaned_data.get('image')
        if img:
            # limit size to 2.5 MB
            max_size = 2.5 * 1024 * 1024
            if img.size > max_size:
                raise forms.ValidationError('Файл занадто великий. Максимум 2.5 MB.')
            # basic content-type check
            if not getattr(img, 'content_type', '').startswith('image/'):
                raise forms.ValidationError('Невірний формат файлу. Очікується зображення.')
        return img


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text', 'is_correct', 'image')

    def clean_image(self):
        img = self.cleaned_data.get('image')
        if img:
            max_size = 2.5 * 1024 * 1024
            if img.size > max_size:
                raise forms.ValidationError('Файл занадто великий. Максимум 2.5 MB.')
            if not getattr(img, 'content_type', '').startswith('image/'):
                raise forms.ValidationError('Невірний формат файлу. Очікується зображення.')
        return img

# Answer formset for adding answers to the initial question
from django.forms import modelformset_factory
AnswerFormSet = modelformset_factory(
    Answer,
    form=AnswerForm,
    fields=('text', 'is_correct', 'image'),
    extra=2,
    min_num=2,
    validate_min=True,
    can_delete=False,
)
