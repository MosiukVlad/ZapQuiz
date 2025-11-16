from django.urls import path
from . import views

urlpatterns = [
    path('', views.QuizListView.as_view(), name='index'),
    path('quiz/<int:quiz_id>/start/', views.QuizDetailView.as_view(), name='start_quiz'),
    path('quiz/session/<int:session_id>/question/<int:question_number>/', views.QuizSessionView.as_view(), name='quiz_question'),
    path('quiz/session/<int:session_id>/submit/<int:question_id>/', views.QuizSessionView.as_view(), name='submit_answer'),
    path('quiz/session/<int:session_id>/results/', views.QuizSessionView.as_view(), name='quiz_results'),
    path('quiz/<int:quiz_id>/leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
]