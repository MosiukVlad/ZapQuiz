from django.contrib import admin
from .models import Quiz, Question, Answer, PlayerAnswer, QuizSession

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    max_num = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ('quiz', 'text', 'question_type', 'order', 'points')
    list_filter = ('quiz', 'question_type')
    ordering = ('quiz', 'order')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # якщо редагуємо існуюче питання
            if obj.question_type == 'binary':
                self.inlines[0].max_num = 2
                self.inlines[0].min_num = 2
            else:
                self.inlines[0].max_num = 4
                self.inlines[0].min_num = 4
        return form

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'time_limit', 'is_active')
    list_filter = ('is_active', 'created_at')
    inlines = [QuestionInline]

class PlayerAnswerAdmin(admin.ModelAdmin):
    list_display = ('player', 'question', 'answer', 'points_earned', 'response_time')
    list_filter = ('player', 'question__quiz')

class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'player', 'start_time', 'end_time', 'total_score')
    list_filter = ('quiz', 'player')

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(PlayerAnswer, PlayerAnswerAdmin)
admin.site.register(QuizSession, QuizSessionAdmin)
