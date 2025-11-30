from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Quiz, Question, Answer, HostedGame, HostedParticipant
from results.models import QuizSession, PlayerAnswer
from django.db.models import Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Create your views here.

class QuizListView(View):
    def get(self, request):
        quizzes = Quiz.objects.filter(is_active=True)
        return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})


from .forms import QuizCreateForm
import json

from django.views import View as BaseView
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import secrets, string
from results.models import QuizSession


class QuizCreateView(LoginRequiredMixin, View):
    template_name = 'quiz/quiz_form.html'
    success_url = reverse_lazy('index')

    def get(self, request):
        quiz_form = QuizCreateForm()
        # import question form and answer formset declared in forms.py
        from .forms import QuestionForm as QF, AnswerFormSet
        qform = QF(prefix='q0')
        answer_formset = AnswerFormSet(queryset=Answer.objects.none(), prefix='a0')
        return render(request, self.template_name, {'form': quiz_form, 'question_form': qform, 'answer_formset': answer_formset})

    def post(self, request):
        # Support new client-side flow: questions are posted as JSON in 'questions_json'
        questions_json = request.POST.get('questions_json')
        if questions_json:
            try:
                questions = json.loads(questions_json)
            except Exception:
                return render(request, self.template_name, {'form': QuizCreateForm(request.POST), 'error': 'Невірний формат даних питань'})

            # Validate structure: at least 1 question, each has text and >=2 answers
            if not isinstance(questions, list) or len(questions) < 1:
                return render(request, self.template_name, {'form': QuizCreateForm(request.POST), 'error': 'Потрібно додати принаймні 1 питання'})

            for q in questions:
                if not q.get('text'):
                    return render(request, self.template_name, {'form': QuizCreateForm(request.POST), 'error': 'Кожне питання повинно містити текст'})
                answers = q.get('answers') or []
                if len([a for a in answers if a.get('text')]) < 2:
                    return render(request, self.template_name, {'form': QuizCreateForm(request.POST), 'error': 'Кожне питання повинно мати принаймні 2 відповіді'})

            # Validate and save quiz
            quiz_form = QuizCreateForm(request.POST)
            if not quiz_form.is_valid():
                return render(request, self.template_name, {'form': quiz_form, 'error': 'Помилка в полях вікторини'})

            quiz = quiz_form.save(commit=False)
            quiz.creator = request.user
            quiz.is_active = True
            quiz.save()

            # Create questions and answers
            for idx, q in enumerate(questions, start=1):
                # attach uploaded image if present; client uses keys like q0_image, q0_a0_image
                q_image_key = f"q{idx-1}_image"
                q_image = request.FILES.get(q_image_key)
                question = Question.objects.create(quiz=quiz, text=q.get('text'), order=idx, image=q_image)
                for ai, a in enumerate(q.get('answers', [])):
                    if not a.get('text'):
                        continue
                    a_image_key = f"q{idx-1}_a{ai}_image"
                    a_image = request.FILES.get(a_image_key)
                    Answer.objects.create(question=question, text=a.get('text'), is_correct=bool(a.get('is_correct')), image=a_image)

            return redirect(self.success_url)

        # Fallback: legacy single-question flow (if present)
        from .forms import QuestionForm as QF, AnswerFormSet
        quiz_form = QuizCreateForm(request.POST)
        qform = QF(request.POST, request.FILES, prefix='q0')
        answer_formset = AnswerFormSet(request.POST, request.FILES, queryset=Answer.objects.none(), prefix='a0')

        # Validate quiz form (always required)
        if not quiz_form.is_valid():
            # If the main quiz form is invalid, return with errors
            return render(request, self.template_name, {'form': quiz_form, 'question_form': qform, 'answer_formset': answer_formset})

        # At this point the quiz form is valid. We'll save the Quiz regardless of whether
        # legacy question/answer fields are present or valid. If the question form and
        # answer formset are valid and contain >=2 answers, we'll also create the question
        # and its answers. This makes the Create button functional even when the client
        # UI hides the legacy fields (no JSON flow used).
        quiz = quiz_form.save(commit=False)
        quiz.creator = request.user
        quiz.is_active = True
        quiz.save()

        # Try to save an initial question + answers if provided and valid
        answers_clean = []
        if qform.is_valid() and answer_formset.is_valid():
            answers_clean = [f for f in answer_formset.cleaned_data if f and f.get('text')]
            if answers_clean and len(answers_clean) >= 2:
                question = qform.save(commit=False)
                question.quiz = quiz
                question.save()
                for ans_data in answers_clean:
                    Answer.objects.create(question=question, text=ans_data.get('text'), is_correct=ans_data.get('is_correct', False))

        return redirect(self.success_url)


class JoinView(BaseView):
    """Main page: join a quiz by code."""
    template_name = 'quiz/join.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        code = request.POST.get('code', '').strip()
        if not code:
            return render(request, self.template_name, {'error': 'Введіть код вікторини'})
        try:
            quiz = Quiz.objects.get(code__iexact=code, is_active=True)
        except Quiz.DoesNotExist:
            return render(request, self.template_name, {'error': 'Вікторина з таким кодом не знайдена'})

        # require login to join; redirect to login if anonymous
        if not request.user.is_authenticated:
            # forward next to join with code so after login we continue
            login_url = reverse('login')
            return redirect(f"{login_url}?next={request.path}")

        # create a session and redirect to first question
        session = QuizSession.objects.create(user=request.user, quiz=quiz)
        return redirect('quiz_question', session_id=session.id, question_number=1)


@login_required
def host_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # only creator or staff can host a run
    if not (request.user == quiz.creator or request.user.is_staff):
        return render(request, 'quiz/forbidden.html', status=403)
    # always create a new hosted game so host can run multiple rounds
    alphabet = string.ascii_uppercase + string.digits
    hosted = None
    for _ in range(50):
        candidate = ''.join(secrets.choice(alphabet) for _ in range(6))
        if not Quiz.objects.filter(code=candidate).exists() and not HostedGame.objects.filter(run_code=candidate).exists():
            hosted = HostedGame.objects.create(quiz=quiz, host=request.user, run_code=candidate)
            break
    if hosted is None:
        hosted = HostedGame.objects.create(quiz=quiz, host=request.user, run_code='HOSTED')

    participants = hosted.participants.select_related('user')
    return render(request, 'quiz/host_lobby.html', {'hosted': hosted, 'participants': participants})


@login_required
def join_hosted(request):
    if request.method == 'POST':
        run_code = request.POST.get('run_code', '').strip()
        if not run_code:
            return render(request, 'quiz/host_join.html', {'error': 'Введіть код лобі'})
        try:
            hosted = HostedGame.objects.get(run_code__iexact=run_code)
        except HostedGame.DoesNotExist:
            return render(request, 'quiz/host_join.html', {'error': 'Лобі не знайдено'})

        # ensure user is logged in
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        # add participant
        HostedParticipant.objects.get_or_create(hosted_game=hosted, user=request.user)
        # redirect to lobby view
        return redirect('host_lobby', hosted.id)
    return render(request, 'quiz/host_join.html')


@login_required
def host_lobby(request, hosted_id):
    hosted = get_object_or_404(HostedGame, id=hosted_id)
    # only host or staff can view host control (participants can also view but no controls)
    participants = hosted.participants.select_related('user')
    if request.method == 'POST' and request.user == hosted.host:
        action = request.POST.get('action')
        if action == 'start' and not hosted.is_started and not hosted.is_closed:
            # start the hosted game: create QuizSession for each participant and attach
            for p in participants:
                if p.session is None:
                    session = QuizSession.objects.create(user=p.user, quiz=hosted.quiz)
                    p.session = session
                    p.save()
            hosted.is_started = True
            hosted.save()
            return redirect('host_lobby', hosted.id)
        elif action == 'close' and not hosted.is_started:
            hosted.is_closed = True
            hosted.save()
            return redirect('host_lobby', hosted.id)

    return render(request, 'quiz/host_lobby.html', {'hosted': hosted, 'participants': participants})


@login_required
def host_status(request, hosted_id):
    """Return JSON status for a hosted game, used by participants to auto-redirect when started."""
    hosted = get_object_or_404(HostedGame, id=hosted_id)
    # find participant row for current user
    try:
        p = HostedParticipant.objects.get(hosted_game=hosted, user=request.user)
    except HostedParticipant.DoesNotExist:
        p = None

    data = {
        'is_started': hosted.is_started,
        'is_closed': hosted.is_closed,
        'participant_session_id': p.session.id if p and p.session else None,
    }
    from django.http import JsonResponse
    return JsonResponse(data)


@login_required
def edit_quiz_questions(request, quiz_id):
    """Allow the quiz creator to add/edit questions for a quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # only creator or staff can edit
    if not (request.user == quiz.creator or request.user.is_staff):
        return render(request, 'quiz/forbidden.html', status=403)

    QuestionFormSet = inlineformset_factory(Quiz, Question, fields=('text', 'order', 'image'), extra=3, can_delete=True)
    if request.method == 'POST':
        formset = QuestionFormSet(request.POST, request.FILES, instance=quiz)
        if formset.is_valid():
            formset.save()
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        formset = QuestionFormSet(instance=quiz)

    return render(request, 'quiz/quiz_questions_form.html', {'quiz': quiz, 'formset': formset})


@login_required
def edit_question_answers(request, question_id):
    """Allow the quiz creator to add/edit answers for a question."""
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz
    if not (request.user == quiz.creator or request.user.is_staff):
        return render(request, 'quiz/forbidden.html', status=403)

    AnswerFormSet = inlineformset_factory(Question, Answer, fields=('text', 'is_correct', 'image'), extra=4, can_delete=True)
    if request.method == 'POST':
        formset = AnswerFormSet(request.POST, request.FILES, instance=question)
        if formset.is_valid():
            formset.save()
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        formset = AnswerFormSet(instance=question)

    return render(request, 'quiz/question_answers_form.html', {'question': question, 'formset': formset})

@method_decorator(login_required, name='dispatch')
class QuizDetailView(View):
    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.questions.all()
        return render(request, 'quiz/quiz_detail.html', {'quiz': quiz, 'questions': questions})

    def post(self, request, quiz_id):
        """Start a new QuizSession for the logged-in user and redirect to first question."""
        quiz = get_object_or_404(Quiz, id=quiz_id)
        # create a new session
        session = QuizSession.objects.create(user=request.user, quiz=quiz)
        # redirect to first question
        return redirect('quiz_question', session_id=session.id, question_number=1)


class QuizSessionView(View):
    """Render a question within a QuizSession or handle answer submission."""
    def get(self, request, session_id, question_number=None):
        session = get_object_or_404(QuizSession, id=session_id)
        if question_number is not None:
            question = session.quiz.questions.filter(order=question_number).first()
            if not question:
                # quiz finished — mark session completed and compute score if not already set
                if session.completed_at is None:
                    session.completed_at = timezone.now()
                    # compute total score for answers given during this session only
                    total = PlayerAnswer.objects.filter(
                        user=session.user,
                        question__quiz=session.quiz,
                        answered_at__gte=session.started_at,
                        answered_at__lte=session.completed_at,
                    ).aggregate(total=Sum('score'))['total'] or 0
                    session.total_score = total
                    session.save()
                return render(request, 'quiz/quiz_results.html', {'session': session})
            return render(request, 'quiz/quiz_session.html', {'session': session, 'question': question, 'question_number': question_number})
        return render(request, 'quiz/quiz_session.html', {'session': session})

    def post(self, request, session_id, question_id=None):
        session = get_object_or_404(QuizSession, id=session_id)
        if question_id is None:
            return render(request, 'quiz/quiz_session.html', {'session': session, 'error': 'No question specified'})
        answer_id = request.POST.get('answer_id')
        if not answer_id:
            return render(request, 'quiz/quiz_session.html', {'session': session, 'error': 'No answer submitted'})
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            return render(request, 'quiz/quiz_session.html', {'session': session, 'error': 'Answer not found'})

        score = 1 if answer.is_correct else 0
        PlayerAnswer.objects.create(
            user=session.user,
            question=answer.question,
            selected_answer=answer,
            score=score
        )
        session.total_score = PlayerAnswer.objects.filter(user=session.user, question__quiz=session.quiz).aggregate(total=Sum('score'))['total'] or 0
        session.save()

        next_order = answer.question.order + 1
        return redirect('quiz_question', session_id=session.id, question_number=next_order)


class LeaderboardView(View):
    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        top_players = QuizSession.objects.filter(quiz=quiz, completed_at__isnull=False).order_by('-total_score')[:10]
        return render(request, 'quiz/leaderboard.html', {'quiz': quiz, 'top_players': top_players})


def code_leaderboard(request, quiz_id):
    """Leaderboard for players who joined by code (i.e. sessions NOT created as part of a HostedGame)."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # sessions completed for this quiz
    sessions_qs = QuizSession.objects.filter(quiz=quiz, completed_at__isnull=False)
    # find sessions that belong to hosted participants for this quiz
    hosted_session_ids = HostedParticipant.objects.filter(hosted_game__quiz=quiz, session__isnull=False).values_list('session_id', flat=True)
    # exclude hosted sessions to get only code-joined sessions
    code_sessions = sessions_qs.exclude(id__in=hosted_session_ids).order_by('-total_score')[:50]

    return render(request, 'quiz/code_leaderboard.html', {'quiz': quiz, 'sessions': code_sessions})

