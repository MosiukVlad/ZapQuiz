from django.contrib import admin
from .models import Quiz, Question, Answer, PlayerAnswer, QuizSession
# Register your models here.
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_active',)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order')
    search_fields = ('text',)
    list_filter = ('quiz',)
    
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    search_fields = ('text',)
    list_filter = ('is_correct', 'question__quiz')
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)    
admin.site.register(Answer)
admin.site.register(PlayerAnswer)
admin.site.register(QuizSession)
admin.site.register(Answer, AnswerAdmin)

admin.site.register(Answer, AnswerAdmin)
