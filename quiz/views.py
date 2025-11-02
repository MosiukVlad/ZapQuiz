from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Quiz, Question, Answer, PlayerAnswer, QuizSession
from django.db.models import Sum, Count

def index(request):
    """Головна сторінка зі списком доступних вікторин"""
    active_quizzes = Quiz.objects.filter(is_active=True).annotate(
        question_count=Count('questions')
    )
    return render(request, 'quiz/index.html', {
        'quizzes': active_quizzes
    })

@login_required
def start_quiz(request, quiz_id):
    """Початок нової вікторини"""
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
    
    # Створюємо нову сесію для цієї вікторини
    session = QuizSession.objects.create(
        quiz=quiz,
        player=request.user
    )
    
    return redirect('quiz_question', session_id=session.id, question_number=1)

@login_required
def quiz_question(request, session_id, question_number):
    """Показ питання вікторини"""
    session = get_object_or_404(QuizSession, 
                              pk=session_id, 
                              player=request.user,
                              end_time__isnull=True)
    
    question = session.quiz.questions.filter(order=question_number).first()
    
    if not question:
        # Якщо питань більше немає, завершуємо вікторину
        session.finish_quiz()
        return redirect('quiz_results', session_id=session.id)
    
    # Перевіряємо, чи не було вже відповіді на це питання
    if PlayerAnswer.objects.filter(player=request.user, question=question).exists():
        return redirect('quiz_question', session_id=session_id, question_number=question_number + 1)
    
    return render(request, 'quiz/question.html', {
        'session': session,
        'question': question,
        'question_number': question_number,
        'total_questions': session.quiz.questions.count(),
        'time_limit': session.quiz.time_limit
    })

@login_required
def submit_answer(request, session_id, question_id):
    """Обробка відповіді на питання"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    session = get_object_or_404(QuizSession, 
                              pk=session_id, 
                              player=request.user,
                              end_time__isnull=True)
    
    question = get_object_or_404(Question, pk=question_id, quiz=session.quiz)
    response_time = float(request.POST.get('response_time', 0))
    
    # Для питань з множинним вибором
    answer_ids = request.POST.getlist('answers[]')
    
    # Створюємо відповідь для кожного вибраного варіанту
    total_points = 0
    for answer_id in answer_ids:
        answer = get_object_or_404(Answer, pk=answer_id, question=question)
        player_answer = PlayerAnswer.objects.create(
            player=request.user,
            question=question,
            answer=answer,
            response_time=response_time
        )
        total_points += player_answer.points_earned
    
    # Повертаємо результат
    is_correct = all(Answer.objects.get(pk=aid).is_correct for aid in answer_ids)
    return JsonResponse({
        'points': total_points,
        'is_correct': is_correct,
        'next_question': question.order + 1
    })

@login_required
def quiz_results(request, session_id):
    """Показ результатів вікторини"""
    session = get_object_or_404(QuizSession, pk=session_id, player=request.user)
    
    # Отримуємо всі відповіді користувача в цій сесії
    answers = PlayerAnswer.objects.filter(
        player=request.user,
        question__quiz=session.quiz
    ).select_related('question', 'answer')
    
    # Групуємо відповіді за питаннями
    questions_data = {}
    for answer in answers:
        if answer.question_id not in questions_data:
            questions_data[answer.question_id] = {
                'question': answer.question,
                'answers': [],
                'points': 0,
                'is_correct': True
            }
        questions_data[answer.question_id]['answers'].append(answer)
        questions_data[answer.question_id]['points'] += answer.points_earned
        if not answer.answer.is_correct:
            questions_data[answer.question_id]['is_correct'] = False
    
    return render(request, 'quiz/results.html', {
        'session': session,
        'questions_data': questions_data.values(),
        'total_questions': session.quiz.questions.count(),
        'correct_answers': sum(1 for q in questions_data.values() if q['is_correct'])
    })

def leaderboard(request, quiz_id):
    """Таблиця лідерів для конкретної вікторини"""
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    top_sessions = QuizSession.objects.filter(
        quiz=quiz,
        end_time__isnull=False
    ).select_related('player').order_by('-total_score')[:10]
    
    return render(request, 'quiz/leaderboard.html', {
        'quiz': quiz,
        'top_sessions': top_sessions
    })
