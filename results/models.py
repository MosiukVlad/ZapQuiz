from django.db import models
from quiz.models import Quiz, Question, Answer
# Create your models here.
class QuizSession(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_score = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Відповідь"
        verbose_name_plural = "Відповіді"
        
    def __str__(self):
        return f"Сесія {self.user.username} для {self.quiz.title}"

class PlayerAnswer(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    response_time = models.DurationField(null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Відповідь {self.user.username} на {self.question.text}"
