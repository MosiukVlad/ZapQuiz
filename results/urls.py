from django.urls import path
from . import views

urlpatterns = [
    path('results/session/<int:session_id>/question/<int:question_number>/', views.QuizSessionView.as_view(), name='quiz_question'),
    path('results/session/<int:session_id>/submit/<int:question_id>/', views.QuizSessionView.as_view(), name='submit_answer'),
    path('results/session/<int:session_id>/results/', views.QuizSessionView.as_view(), name='quiz_results'),
    path('results/<int:quiz_id>/leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
]