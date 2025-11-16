from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import UserProfile
from quiz.models import QuizSession

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
        player=request.user,
        end_time__isnull=False
    ).order_by('-end_time')
    
    # Рахуємо загальну статистику
    total_quizzes = quiz_sessions.count()
    total_points = quiz_sessions.aggregate(total=models.Sum('total_score'))['total'] or 0
    
    context = {
        'profile': user_profile,
        'quiz_sessions': quiz_sessions,
        'total_quizzes': total_quizzes,
        'total_points': total_points
    }
    return render(request, 'users/profile.html', context)

@login_required
def leaderboard(request):
    # Отримуємо топ-гравців за загальною кількістю балів
    top_players = UserProfile.objects.annotate(
        total_score=models.Sum('user__quizsession__total_score')
    ).order_by('-total_score')[:10]
    
    return render(request, 'users/leaderboard.html', {'top_players': top_players})
