from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

from .utils.pagination import paginate
from .models import Question, Answer, Tag, Profile, QuestionLike
from .forms import SignupForm, AskForm, LoginForm, AnswerForm, ProfileForm


def index(request):
    questions = Question.objects.get_new()
    page_obj = paginate(questions, request)
    return render(request, 'questions/index.html', {'page_obj': page_obj})


def hot(request):
    questions = Question.objects.get_best()
    page_obj = paginate(questions, request)
    return render(request, 'questions/hot.html', {'page_obj': page_obj})


def question(request, question_id):
    question = get_object_or_404(
        Question.objects.question_detailes(),
        pk=question_id
    )
    answers = Answer.objects.with_likes().filter(question=question)
    page_obj = paginate(answers, request)

    form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(author=request.user, question=question)
                return redirect(f'{question.get_absolute_url()}#answer-{answer.id}')
        else:
            form = AnswerForm()

    return render(request, 'questions/question.html', {
        'curent_question': question,
        'answers': page_obj,
        'form': form,
    })


def tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.get_by_tag(tag.name)
    page_obj = paginate(questions, request)
    return render(request, 'questions/tag.html', {
        'page_obj': page_obj,
        'tag': tag,
    })


def signup(request):
    error = ""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
        else:
            error = "В форме присутствуют ошибки!"
    else:
        form = SignupForm()
    return render(request, 'questions/signup.html', {'form': form, 'error': error})


def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next') or '/'
    error = ''
    form = LoginForm(request.POST or None, request=request)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        if not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts=[request.get_host()]):
            next_url = '/'
        return redirect(next_url)
    elif form.errors:
        error = list(form.non_field_errors())[0] if form.non_field_errors() else ''

    return render(request, 'questions/login.html', {
        'form': form,
        'error': error,
    })


def logout_view(request):
    logout(request)
    next_page = request.META.get('HTTP_REFERER')
    if next_page and url_has_allowed_host_and_scheme(next_page, [request.get_host()]):
        return redirect(next_page)
    return redirect('/')


def ask(request):
    if request.method == 'POST' and request.user.is_authenticated:
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(user=request.user)
            return redirect(question.get_absolute_url())
    else:
        form = AskForm()
    return render(request, 'questions/ask.html', {'form': form})


@login_required
@require_POST
def question_like(request, question_id):

    question = get_object_or_404(
        Question,
        pk=question_id
    )

    QuestionLike.objects.get_or_create(
        question=question,
        user=request.user
    )

    next_url = (
        request.POST.get('next')
        or request.GET.get('next')
        or question.get_absolute_url()
    )

    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
    ):
        next_url = question.get_absolute_url()

    return HttpResponseRedirect(next_url)


@login_required
def profile(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES,
                           instance=request.user.profile)
        if form.is_valid():
            profile = form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return redirect('questions:profile')
    else:
        form = ProfileForm(
            instance=request.user.profile,
            initial={
                'email': request.user.email,
                'nickname': request.user.profile.nickname,
            }
        )
    return render(request, 'questions/profile.html', {'form': form})
