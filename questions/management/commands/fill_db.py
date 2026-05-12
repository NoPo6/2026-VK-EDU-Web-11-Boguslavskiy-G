from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from faker import Faker
import random
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike, Profile

fake = Faker()

class Command(BaseCommand):
    help = "Fill database with fake data"

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int)

    def handle(self, *args, **options):
        ratio = max(options["ratio"], 10)   # минимум 10 пользователей
        users_count = ratio
        tags_count = ratio
        questions_count = ratio * 10
        answers_count = ratio * 100
        likes_count = ratio * 200

        # --- Пользователи ---
        self.stdout.write("Creating users...")
        password = make_password("test123")
        users = [
            User(username=f"user_{i}", email=f"user_{i}@mail.com", password=password)
            for i in range(users_count)
        ]
        User.objects.bulk_create(users, batch_size=5000)
        user_ids = list(User.objects.values_list("id", flat=True))

        # Профили с никнеймами
        self.stdout.write("Creating profiles with nicknames...")
        profiles = []
        for uid in user_ids:
            nickname = fake.user_name()  # генерируем ник
            profiles.append(Profile(user_id=uid, nickname=nickname))
        Profile.objects.bulk_create(profiles, batch_size=5000, ignore_conflicts=True)

        # --- Профили ---
        self.stdout.write("Creating profiles...")
        profiles = [Profile(user_id=uid) for uid in user_ids]
        Profile.objects.bulk_create(profiles, batch_size=5000, ignore_conflicts=True)

        # --- Теги (динамические) ---
        self.stdout.write("Creating tags...")
        tags = []
        for _ in range(tags_count):
            tags.append(Tag(name=fake.unique.word()))
        Tag.objects.bulk_create(tags, batch_size=5000)
        tag_ids = list(Tag.objects.values_list("id", flat=True))

        # --- Вопросы ---
        self.stdout.write("Creating questions...")
        questions = []
        for _ in range(questions_count):
            questions.append(Question(
                title=fake.sentence(nb_words=6)[:255],
                text=fake.text(max_nb_chars=300),
                author_id=random.choice(user_ids),
            ))
        Question.objects.bulk_create(questions, batch_size=5000)
        question_ids = list(Question.objects.values_list("id", flat=True))

        # --- Связи вопрос-тег (по батчам) ---
        self.stdout.write("Creating question-tag relations...")
        through = Question.tags.through
        relations = []
        for qid in question_ids:
            tags_for_question = random.sample(tag_ids, min(3, len(tag_ids)))
            for tid in tags_for_question:
                relations.append(through(question_id=qid, tag_id=tid))
                if len(relations) >= 10000:
                    through.objects.bulk_create(relations, batch_size=10000, ignore_conflicts=True)
                    relations = []
        if relations:
            through.objects.bulk_create(relations, batch_size=10000, ignore_conflicts=True)

        # --- Ответы ---
        self.stdout.write("Creating answers...")
        answers = []
        for _ in range(answers_count):
            answers.append(Answer(
                text=fake.text(max_nb_chars=200),
                author_id=random.choice(user_ids),
                question_id=random.choice(question_ids),
            ))
            if len(answers) >= 10000:
                Answer.objects.bulk_create(answers, batch_size=10000)
                answers = []
        if answers:
            Answer.objects.bulk_create(answers, batch_size=10000)
        answer_ids = list(Answer.objects.values_list("id", flat=True))

        # --- Лайки вопросов (батчами) ---
        self.stdout.write("Creating question likes...")
        q_likes = []
        for _ in range(likes_count // 2):
            q_likes.append(QuestionLike(
                question_id=random.choice(question_ids),
                user_id=random.choice(user_ids),
            ))
            if len(q_likes) >= 10000:
                QuestionLike.objects.bulk_create(q_likes, batch_size=10000, ignore_conflicts=True)
                q_likes = []
        if q_likes:
            QuestionLike.objects.bulk_create(q_likes, batch_size=10000, ignore_conflicts=True)

        # --- Лайки ответов (батчами) ---
        self.stdout.write("Creating answer likes...")
        a_likes = []
        for _ in range(likes_count // 2):
            a_likes.append(AnswerLike(
                answer_id=random.choice(answer_ids),
                user_id=random.choice(user_ids),
            ))
            if len(a_likes) >= 10000:
                AnswerLike.objects.bulk_create(a_likes, batch_size=10000, ignore_conflicts=True)
                a_likes = []
        if a_likes:
            AnswerLike.objects.bulk_create(a_likes, batch_size=10000, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("Database filled!"))