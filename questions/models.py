from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Менеджер моделей
class ModelManager(models.Manager):
    def get_new(self):
        return self.select_related('author').prefetch_related('tags').order_by('-created_at')

    def get_best(self):
        return self.select_related('author').prefetch_related('tags').annotate(
            likes_count=models.Count('likes')
        ).order_by('-likes_count')

    def get_by_tag(self, tag_name):
        return self.select_related('author').prefetch_related('tags').filter(
            tags__name=tag_name
        ).order_by('-created_at')


# Таблица с профилями
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    nickname = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.user.username


# Таблица с тэгами 
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
    

# Таблица вопросов
class Question(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст вопроса')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    tags = models.ManyToManyField(Tag, related_name='questions', through='QuestionTag')

    objects = ModelManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('question_detail', args=[self.pk])


# Таблица овтетов
class Answer(models.Model):
    text = models.TextField(verbose_name='Текст ответа')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Ответ на "{self.question.title}"'


# Таблица связи лайков вопросов и юзеров
class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'
        constraints = [
            models.UniqueConstraint(fields=['question', 'user'], name='unique_question_like')
        ]


# Таблица связи лайков ответов и юзеров
class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
        constraints = [
            models.UniqueConstraint(fields=['answer', 'user'], name='unique_answer_like')
        ]


# Таблица связи тегов и вопросов
class QuestionTag(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('question', 'tag')
        verbose_name = 'Тег вопроса'
        verbose_name_plural = 'Теги вопросов'
