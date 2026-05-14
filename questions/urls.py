from django.urls import path
from questions import views

app_name = 'questions'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot', views.hot, name='hot'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('signup', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('ask/', views.ask, name='ask'),
    path('signup', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('question/<int:question_id>/like/', views.question_like, name='question_like'),
]
