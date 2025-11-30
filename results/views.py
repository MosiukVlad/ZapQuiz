from django.shortcuts import render
from django.views import View
from.models import Quiz, Question, Answer
from .models import QuizSession, PlayerAnswer
from django.db.models import Sum
from django.contrib.auth.models import User
# Create your views here.
class QuizSessionView(View):
    def get(self, request, session_id, question_number=None):
        """If question_number is provided, render that question for the session.
        Otherwise render the session overview.
        """
        session = QuizSession.objects.get(id=session_id)
        if question_number is not None:
            question = session.quiz.questions.filter(order=question_number).first()
            if not question:
                # no more questions -> show results
                return render(request, 'quiz/quiz_results.html', {'session': session})
            return render(request, 'quiz/quiz_session.html', {'session': session, 'question': question, 'question_number': question_number})
        return render(request, 'quiz/quiz_session.html', {'session': session})

    def post(self, request, session_id, question_id=None):
        """Handle answer submission for a question (basic implementation).
        Expects POST param 'answer_id'.
        """
        session = QuizSession.objects.get(id=session_id)
        if question_id is None:
            return render(request, 'quiz/quiz_session.html', {'session': session, 'error': 'No question specified'})
        # fetch posted answer
        answer_id = request.POST.get('answer_id')
        if not answer_id:
            return render(request, 'quiz/quiz_session.html', {'session': session, 'error': 'No answer submitted'})
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            return render(request, 'quiz/quiz_session.html', {'session': session, 'error': 'Answer not found'})

        # save PlayerAnswer (simple scoring: 1 for correct)
        score = 1 if answer.is_correct else 0
        PlayerAnswer.objects.create(
            user=session.user,
            question=answer.question,
            selected_answer=answer,
            score=score
        )
        # increment session total score
        session.total_score = PlayerAnswer.objects.filter(user=session.user, question__quiz=session.quiz).aggregate(total=Sum('score'))['total'] or 0
        session.save()

        # redirect to next question
        next_order = answer.question.order + 1
        return render(request, 'results/quiz_session.html', {'session': session, 'message': 'Answer recorded', 'next_question': next_order})

class LeaderboardView(View):
    def get(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        top_players = QuizSession.objects.filter(quiz=quiz).order_by('-total_score')[:10]
        return render(request, 'results/leaderboard.html', {'quiz': quiz, 'top_players': top_players})