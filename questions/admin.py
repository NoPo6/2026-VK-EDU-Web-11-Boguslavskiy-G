from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.text import Truncator
from .models import (
    Profile, Tag, Question, Answer,
    QuestionLike, AnswerLike, QuestionTag
)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'
    fields = ('avatar', 'nickname')


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_nickname')
    search_fields = ('username', 'email', 'profile__nickname')

    def get_nickname(self, obj):
        return obj.profile.nickname
    
    get_nickname.short_description = 'Никнейм'
    get_nickname.admin_order_field = 'profile__nickname'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'avatar')
    search_fields = ('user__username', 'nickname')
    list_filter = ('user__is_active',)
    raw_id_fields = ('user',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'question_count')
    search_fields = ('name',)
    list_filter = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(q_count=Count('questions'))

    def question_count(self, obj):
        return obj.q_count
    
    question_count.short_description = 'Кол-во вопросов'


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    fields = ('author', 'text', 'is_correct', 'created_at')
    readonly_fields = ('created_at',)
    raw_id_fields = ('author',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ('title', 'author', 'created_at', 'tags_list', 'likes_count')
    search_fields = ('title', 'author__username', 'text')
    list_filter = ('created_at',)
    list_select_related = ('author',)
    raw_id_fields = ('author',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(likes_cnt=Count('likes'))

    def tags_list(self, obj):
        return ', '.join([t.name for t in obj.tags.all()])
    tags_list.short_description = 'Теги'

    def likes_count(self, obj):
        return obj.likes_cnt
    
    likes_count.short_description = 'Лайки'
    likes_count.admin_order_field = 'likes_cnt'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'question', 'author', 'is_correct', 'created_at')
    search_fields = ('text', 'author__username', 'question__title')
    list_filter = ('is_correct', 'created_at', 'question')
    list_select_related = ('question', 'author')
    raw_id_fields = ('question', 'author')

    def short_text(self, obj):
        return Truncator(obj.text).chars(50)
    
    short_text.short_description = 'Текст ответа'


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('question', 'user')
    search_fields = ('question__title', 'user__username')
    list_filter = ('question', 'user')
    raw_id_fields = ('question', 'user')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('answer', 'user')
    search_fields = ('answer__text', 'user__username')
    list_filter = ('answer', 'user')
    raw_id_fields = ('answer', 'user')


@admin.register(QuestionTag)
class QuestionTagAdmin(admin.ModelAdmin):
    list_display = ('question', 'tag')
    raw_id_fields = ('question', 'tag')