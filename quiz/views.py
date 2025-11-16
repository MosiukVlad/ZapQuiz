from django.shortcuts import render
from django.views import View
from .models import Quiz, Question, Answer, PlayerAnswer, QuizSession
# Create your views here.

class QuizListView(View):
    def get(self, request):
        quizzes = Quiz.objects.filter(is_active=True)
        return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})

class QuizDetailView(View):
    def get(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        questions = quiz.questions.all()
        return render(request, 'quiz/quiz_detail.html', {'quiz': quiz, 'questions': questions})

class QuizSessionView(View):
    def get(self, request, session_id):
        session = QuizSession.objects.get(id=session_id)
        return render(request, 'quiz/quiz_session.html', {'session': session})
    def post(self, request, session_id):
        session = QuizSession.objects.get(id=session_id)
        # Handle answer submission logic here
        return render(request, 'quiz/quiz_session.html', {'session': session})

class LeaderboardView(View):
    def get(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        top_players = competitors.objects.filter(quiz=quiz).order_by('-score')[:10]
        return render(request, 'quiz/leaderboard.html', {'quiz': quiz, 'top_players': top_players})
