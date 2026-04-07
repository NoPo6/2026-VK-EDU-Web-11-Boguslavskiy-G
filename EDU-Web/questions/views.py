from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from datetime import datetime

QUESTIONS = [
    {
        'title': f'Question title{i}',
        'text': f'Text {i}',
        'answers': f'answers({100})',
        'date': f'{datetime.now().strftime("%d.%m.%Y %H:%M")}',
        'question_number': i,
    }
    for i in range(100)
]

# Create your views here.
# отработка ошибок пагинации
def paginate(objects_list, request, per_page = 20):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page

def index(request):
    page_obj = paginate(QUESTIONS, request, per_page=20)
    return render(request, 'questions/index.html', context={'questions': page_obj.object_list, 'page_obj': page_obj})

def hot(request):
    page_obj = paginate(QUESTIONS, request, per_page=20)
    return render(request, 'questions/hot.html', context={'questions': page_obj.object_list, 'page_obj': page_obj})

def question(request, question_number):
    page_obj = paginate(QUESTIONS, request, per_page=20)
    curent_question = QUESTIONS[int(question_number)]
    return render(request, 'questions/question.html', context={'questions': page_obj.object_list, 'page_obj': page_obj, 
                                                               'question_number': question_number, 'curent_question': curent_question})

def tag(request, tag_name):
    page_obj = paginate(QUESTIONS, request, per_page=20)
    return render(request, 'questions/tag.html', context={'questions': page_obj.object_list, 'page_obj': page_obj, 'tag_name': tag_name})

def login(request):
    return render(request, 'questions/login.html')

def signup(request):
    return render(request, 'questions/signup.html')

def profile(request):
    return render(request, 'questions/profile.html')

def ask(request):
    return render(request, 'questions/ask.html')
