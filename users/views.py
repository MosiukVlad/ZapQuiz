from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import UserProfile
from results.models import QuizSession
from django.db import models
from django.db.models.functions import Coalesce
from quiz.models import Quiz

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматично входимо в систему після реєстрації
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    # Отримуємо всі сесії вікторин користувача
    quiz_sessions = QuizSession.objects.filter(
        user=request.user,
        completed_at__isnull=False
    ).order_by('-completed_at')
    
    # Рахуємо загальну статистику
    total_quizzes = quiz_sessions.count()
    total_points = quiz_sessions.aggregate(total=models.Sum('total_score'))['total'] or 0
    
    context = {
        'profile': user_profile,
        'quiz_sessions': quiz_sessions,
        'total_quizzes': total_quizzes,
        'total_points': total_points
    }
    # quizzes created by this user
    created_quizzes = Quiz.objects.filter(creator=request.user).order_by('-created_at')
    context['created_quizzes'] = created_quizzes
    return render(request, 'users/profile.html', context)

@login_required
def leaderboard(request):
    # Отримуємо топ-гравців за загальною кількістю балів
    # Анотуємо: сумарні бали, кількість завершених сесій та середній бал
    top_players = (
        UserProfile.objects.annotate(
            total_score=Coalesce(
                models.Sum(
                    'user__quizsession__total_score',
                    filter=models.Q(user__quizsession__completed_at__isnull=False)
                ),
                0,
                output_field=models.IntegerField(),
            ),
            num_sessions=Coalesce(
                models.Count(
                    'user__quizsession',
                    filter=models.Q(user__quizsession__completed_at__isnull=False)
                ),
                0,
                output_field=models.IntegerField(),
            ),
            avg_score=Coalesce(
                models.Avg(
                    'user__quizsession__total_score',
                    filter=models.Q(user__quizsession__completed_at__isnull=False)
                ),
                0.0,
                output_field=models.FloatField(),
            ),
        )
        .order_by('-total_score', '-avg_score')[:20]
    )

    context = {
        'top_players': top_players,
        'user': request.user,
    }
    return render(request, 'users/leaderboard.html', context)
