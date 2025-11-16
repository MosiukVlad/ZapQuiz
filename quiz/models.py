from django.db import models
# Create your models here.
class Quiz(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва вікторини")
    description = models.TextField(blank=True, verbose_name="Опис вікторини")
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
    is_correct = models.BooleanField(default=False, verbose_name="Правильна відповідь")
    
    def __str__(self):
        return f"Відповідь на {self.question.text}"

    class Meta:
        verbose_name = "Відповідь"
        verbose_name_plural = "Відповіді"

class competitors(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"

    class Meta:
        verbose_name = "Учасник"
        verbose_name_plural = "Учасники"

class PlayerAnswer(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    response_time = models.DurationField(null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Відповідь {self.user.username} на {self.question.text}"

class QuizSession(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_score = models.IntegerField(default=0)

    def __str__(self):
        return f"Сесія {self.user.username} для {self.quiz.title}"