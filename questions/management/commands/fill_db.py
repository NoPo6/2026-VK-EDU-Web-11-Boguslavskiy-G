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
        ratio = max(options["ratio"], 10)
        users_count = ratio
        tags_count = ratio
        questions_count = ratio * 10
        answers_count = ratio * 100
        likes_count = ratio * 200

        self.stdout.write("Creating users...")
        password = make_password("test123")
        users = [
            User(username=f"user_{i}", email=f"user_{i}@mail.com", password=password)
            for i in range(users_count)
        ]
        User.objects.bulk_create(users, batch_size=5000)
        user_ids = list(User.objects.values_list("id", flat=True))

        self.stdout.write("Creating profiles with nicknames...")
        profiles = [
            Profile(user_id=uid, nickname=fake.user_name())
            for uid in user_ids
        ]
        Profile.objects.bulk_create(profiles, batch_size=5000, ignore_conflicts=True)

        self.stdout.write("Creating tags...")
        tags = []
        used = set()
        for _ in range(tags_count):
            name = fake.word()
            if name in used:
                name = f"{name}_{random.randint(1, 999999)}"
            used.add(name)
            tags.append(Tag(name=name))
        Tag.objects.bulk_create(tags, batch_size=5000)
        tag_ids = list(Tag.objects.values_list("id", flat=True))

        self.stdout.write("Creating questions...")
        questions = [
            Question(
                title=fake.sentence(nb_words=6)[:255],
                text=fake.text(max_nb_chars=300),
                author_id=random.choice(user_ids),
            )
            for _ in range(questions_count)
        ]
        Question.objects.bulk_create(questions, batch_size=5000)
        question_ids = list(Question.objects.values_list("id", flat=True))

        self.stdout.write("Creating question-tag relations...")
        through = Question.tags.through
        relations = []

        for qid in question_ids:
            for tid in random.sample(tag_ids, min(3, len(tag_ids))):
                relations.append(through(question_id=qid, tag_id=tid))

                if len(relations) >= 10000:
                    through.objects.bulk_create(relations, batch_size=10000, ignore_conflicts=True)
                    relations = []

        if relations:
            through.objects.bulk_create(relations, batch_size=10000, ignore_conflicts=True)

        self.stdout.write("Creating answers...")
        answers = [
            Answer(
                text=fake.text(max_nb_chars=200),
                author_id=random.choice(user_ids),
                question_id=random.choice(question_ids),
            )
            for _ in range(answers_count)
        ]

        Answer.objects.bulk_create(answers, batch_size=10000)
        answer_ids = list(Answer.objects.values_list("id", flat=True))

        self.stdout.write("Creating question likes...")
        q_likes = [
            QuestionLike(
                question_id=random.choice(question_ids),
                user_id=random.choice(user_ids),
            )
            for _ in range(likes_count // 2)
        ]

        QuestionLike.objects.bulk_create(q_likes, batch_size=10000, ignore_conflicts=True)

        self.stdout.write("Creating answer likes...")
        a_likes = [
            AnswerLike(
                answer_id=random.choice(answer_ids),
                user_id=random.choice(user_ids),
            )
            for _ in range(likes_count // 2)
        ]

        AnswerLike.objects.bulk_create(a_likes, batch_size=10000, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("Database filled!"))