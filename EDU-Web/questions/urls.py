from django.urls import path
from questions import views

app_name = 'questions'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot', views.hot, name='hot'),
    path('question/<str:question_number>/', views.question, name='question'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('profile', views.profile, name='profile'),
    path('ask', views.ask, name='ask'),
]
