from django.shortcuts import render, get_object_or_404
from .utils.pagination import paginate
from .models import Question, Answer, Tag

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
        Question.objects.select_related('author').prefetch_related('tags'),
        pk=question_id
    )
    answers = Answer.objects.filter(question=question).select_related('author')
    page_obj = paginate(answers, request)
    return render(request, 'questions/question.html', {
        'curent_question': question,
        'answers': page_obj,
    })

def tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.get_by_tag(tag.name)
    page_obj = paginate(questions, request)
    return render(request, 'questions/tag.html', {
        'page_obj': page_obj,
        'tag': tag,
    })

def login(request):
    return render(request, 'questions/login.html')

def signup(request):
    return render(request, 'questions/signup.html')

def profile(request):
    return render(request, 'questions/profile.html')

def ask(request):
    return render(request, 'questions/ask.html')