from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class QuestionType(models.TextChoices):
    BINARY = 'binary', 'True/False або 2 варіанти (1 правильний)'
    SINGLE = 'single', '4 варіанти (1 правильний)'
    MULTIPLE = 'multiple', '4 варіанти (декілька правильних)'

class Quiz(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва вікторини")
    description = models.TextField(blank=True, verbose_name="Опис")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    time_limit = models.IntegerField(
        help_text="Обмеження часу на кожне питання (в секундах)", 
        default=20,
        verbose_name="Ліміт часу"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вікторина"
        verbose_name_plural = "Вікторини"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name="Вікторина")
    text = models.TextField(verbose_name="Текст питання")
    question_type = models.CharField(
        max_length=10,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE,
        verbose_name="Тип питання"
    )
    points = models.IntegerField(default=1000, verbose_name="Бали")
    order = models.IntegerField(default=0, verbose_name="Порядковий номер")
    image = models.ImageField(
        upload_to='quiz_images/', 
        null=True, 
        blank=True,
        verbose_name="Зображення"
    )
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Перевірка кількості правильних відповідей відповідно до типу питання
        correct_answers = self.answers.filter(is_correct=True).count()
        if self.question_type == QuestionType.BINARY:
            if self.answers.count() != 2:
                raise ValidationError('Для типу True/False повинно бути рівно 2 варіанти відповіді')
            if correct_answers != 1:
                raise ValidationError('Для типу True/False повинна бути рівно 1 правильна відповідь')
        elif self.question_type == QuestionType.SINGLE:
            if self.answers.count() != 4:
                raise ValidationError('Для питання з одною правильною відповіддю повинно бути рівно 4 варіанти')
            if correct_answers != 1:
                raise ValidationError('Повинна бути рівно 1 правильна відповідь')
        elif self.question_type == QuestionType.MULTIPLE:
            if self.answers.count() != 4:
                raise ValidationError('Для питання з декількома правильними відповідями повинно бути рівно 4 варіанти')
            if correct_answers < 2:
                raise ValidationError('Повинно бути як мінімум 2 правильні відповіді')
    
    def __str__(self):
        return f"{self.quiz.title} - Питання {self.order}"
    
    class Meta:
        verbose_name = "Питання"
        verbose_name_plural = "Питання"
        ordering = ['quiz', 'order']

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="Питання")
    text = models.CharField(max_length=200, verbose_name="Текст відповіді")
    is_correct = models.BooleanField(default=False, verbose_name="Правильна відповідь")
    
    def __str__(self):
        return f"{self.text} ({'Правильна' if self.is_correct else 'Неправильна'})"
    
    class Meta:
        verbose_name = "Відповідь"
        verbose_name_plural = "Відповіді"

class PlayerAnswer(models.Model):
    player = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    response_time = models.FloatField(help_text="Response time in seconds")
    points_earned = models.IntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)

    def calculate_points(self):
        if self.answer.is_correct:
            # Calculate points based on response time (faster = more points)
            max_points = self.question.points
            time_factor = max(0, (self.question.quiz.time_limit - self.response_time) / self.question.quiz.time_limit)
            return int(max_points * time_factor)
        return 0

    def save(self, *args, **kwargs):
        if not self.points_earned:
            self.points_earned = self.calculate_points()
        super().save(*args, **kwargs)

class QuizSession(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    player = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_score = models.IntegerField(default=0)
    
    def finish_quiz(self):
        self.end_time = timezone.now()
        self.total_score = PlayerAnswer.objects.filter(
            player=self.player,
            question__quiz=self.quiz
        ).aggregate(total=models.Sum('points_earned'))['total'] or 0
        self.save()
