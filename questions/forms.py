from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Question, Tag, Answer, Profile
from django.contrib.auth import authenticate


class SignupForm(UserCreationForm):
    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите логин'})
    )
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите почту'})
    )
    nickname = forms.CharField(
        required=True,          
        label='',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ник'})
    )
    password1 = forms.CharField(
        label='', strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )
    password2 = forms.CharField(
        label='', strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2') 

    def save(self, commit=True):
        user = super().save(commit=commit)  
        if commit:
            nickname = self.cleaned_data.get('nickname', '')
            Profile.objects.update_or_create(
                user=user,
                defaults={'nickname': nickname}
            )
        return user


class AskForm(forms.ModelForm):
    tags_str = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите теги через запятую',
        }),
        label='Теги'
    )

    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Заголовок вопроса',
        }),
        label=''  
    )

    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Текст вопроса',
            'rows': 5,
        }),
        label=''
    )

    class Meta:
        model = Question
        fields = ['title', 'text']

    def clean_tags_str(self):
        tag_names = [t.strip() for t in self.cleaned_data['tags_str'].split(',') if t.strip()]
        if len(tag_names) > 10:
            raise forms.ValidationError('Можно указать не более 10 тегов')
        return tag_names

    def save(self, user, commit=True):
        question = super().save(commit=False)
        question.author = user
        if commit:
            question.save()
            tag_names = self.cleaned_data.get('tags_str', [])
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                question.tags.add(tag)
        return question


class LoginForm(forms.Form):
    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите логин',
        })
    )

    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
        })
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password and self.request:
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                raise forms.ValidationError('Sorry, wrong password!')
            self.user_cache = user   
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)


class AnswerForm(forms.ModelForm):
    text = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Введите свой ответ!',
        })
    )

    class Meta:
        model = Answer
        fields = ['text']

    def save(self, commit=True, author=None, question=None):
        answer = super().save(commit=False)
        answer.author = author
        answer.question = question
        if commit:
            answer.save()
        return answer
    

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email',
        })
    )
    nickname = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ник',
        })
    )
    avatar = forms.ImageField(
        required=False,
        label='',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = Profile
        fields = ['nickname', 'avatar']   

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
        return profile