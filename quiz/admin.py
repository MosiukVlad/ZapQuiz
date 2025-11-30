from django.contrib import admin
from .models import Quiz, Question, Answer

# Clean, single registrations and simple ModelAdmin classes
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'is_active', 'created_at')
    search_fields = ('title', 'creator__username')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'quiz', 'order')
    search_fields = ('text',)
    list_filter = ('quiz',)
    ordering = ('quiz', 'order')

    def text_short(self, obj):
        return (obj.text[:75] + '...') if len(obj.text) > 75 else obj.text
    text_short.short_description = 'Текст питання'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'question', 'is_correct')
    search_fields = ('text',)
    list_filter = ('is_correct', 'question__quiz')

    def text_short(self, obj):
        return (obj.text[:75] + '...') if len(obj.text) > 75 else obj.text
    text_short.short_description = 'Текст відповіді'

# Note: QuizSession and PlayerAnswer models aren't imported here; if you add them
# later, register them once (avoid duplicate admin.site.register calls).
# Also: templates for the admin are provided by Django automatically; if you
# meant custom frontend templates for quiz sessions, those should live under
# `quiz/templates/quiz/` and be wired in `quiz/urls.py`/views.
