from django.db import models
# Create your models here.
class Quiz(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва вікторини")
    description = models.TextField(blank=True, verbose_name="Опис вікторини")
    # Short join code for quick access (e.g., ABC123)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name="Код вікторини")
    ACCESS_CHOICES = (
        ('open', 'Open'),
        ('hosted', 'Hosted'),
    )
    access_type = models.CharField(max_length=10, choices=ACCESS_CHOICES, default='open', verbose_name='Тип доступу')
    creator = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='quizzes', verbose_name="Автор")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    time_limit = models.DurationField(null=True, blank=True, verbose_name="Обмеження часу")
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вікторина"
        verbose_name_plural = "Вікторини"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE, verbose_name="Вікторина")
    text = models.TextField(verbose_name="Текст питання")
    # Optional image for the question
    image = models.ImageField(upload_to='questions/%Y/%m/%d/', null=True, blank=True, verbose_name='Зображення питання')
    order = models.PositiveIntegerField(verbose_name="Порядок питання")
    
    def __str__(self):
        return f"Питання {self.order} для {self.quiz.title}"

    class Meta:
        verbose_name = "Питання"
        verbose_name_plural = "Питання"
        ordering = ['order']

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE, verbose_name="Питання")
    text = models.CharField(max_length=500, verbose_name="Текст відповіді")
    # Optional image for the answer
    image = models.ImageField(upload_to='answers/%Y/%m/%d/', null=True, blank=True, verbose_name='Зображення відповіді')
    is_correct = models.BooleanField(default=False, verbose_name="Правильна відповідь")
    
    def __str__(self):
        return f"Відповідь на {self.question.text}"


class HostedGame(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='hosted_games', on_delete=models.CASCADE)
    host = models.ForeignKey('auth.User', related_name='hosted_games', on_delete=models.CASCADE)
    run_code = models.CharField(max_length=8, unique=True)
    is_started = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hosted {self.quiz.title} ({self.run_code})"


class HostedParticipant(models.Model):
    hosted_game = models.ForeignKey(HostedGame, related_name='participants', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='hosted_participations', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey('results.QuizSession', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('hosted_game', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.hosted_game.run_code}"

    


