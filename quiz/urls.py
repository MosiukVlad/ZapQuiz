from django.urls import path
from . import views

urlpatterns = [
    path('', views.JoinView.as_view(), name='index'),
    path('quizzes/', views.QuizListView.as_view(), name='quiz_list'),
    path('quiz/create/', views.QuizCreateView.as_view(), name='quiz_create'),
    path('quiz/<int:quiz_id>/host/', views.host_quiz, name='host_quiz'),
    path('host/join/', views.join_hosted, name='join_hosted'),
    path('host/<int:hosted_id>/lobby/', views.host_lobby, name='host_lobby'),
    path('host/<int:hosted_id>/status/', views.host_status, name='host_status'),
    path('quiz/<int:quiz_id>/start/', views.QuizDetailView.as_view(), name='start_quiz'),
    path('quiz/<int:quiz_id>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('quiz/<int:quiz_id>/questions/', views.edit_quiz_questions, name='edit_quiz_questions'),
    path('quiz/question/<int:question_id>/answers/', views.edit_question_answers, name='edit_question_answers'),
    path('quiz/session/<int:session_id>/question/<int:question_number>/', views.QuizSessionView.as_view(), name='quiz_question'),
    path('quiz/session/<int:session_id>/submit/<int:question_id>/', views.QuizSessionView.as_view(), name='submit_answer'),
    path('quiz/session/<int:session_id>/results/', views.QuizSessionView.as_view(), name='quiz_results'),
    path('quiz/<int:quiz_id>/leaderboard/', views.LeaderboardView.as_view(), name='quiz_leaderboard'),
    path('quiz/<int:quiz_id>/code_leaderboard/', views.code_leaderboard, name='quiz_code_leaderboard'),
]