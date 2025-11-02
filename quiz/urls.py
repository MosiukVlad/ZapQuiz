from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('quiz/session/<int:session_id>/question/<int:question_number>/', views.quiz_question, name='quiz_question'),
    path('quiz/session/<int:session_id>/submit/<int:question_id>/', views.submit_answer, name='submit_answer'),
    path('quiz/session/<int:session_id>/results/', views.quiz_results, name='quiz_results'),
    path('quiz/<int:quiz_id>/leaderboard/', views.leaderboard, name='leaderboard'),
]