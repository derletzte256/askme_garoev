from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from faker import Faker
import random
from django.core.files import File
from pathlib import Path

from app.models import Question, Answer, Tag, QuestionLike, AnswerLike, Profile

class Command(BaseCommand):
    help = 'Fills database with sample data based on ratio'
    BATCH_SIZE = 1000

    def add_arguments(self, parser):
        parser.add_argument(
            'ratio',
            type=int,
            nargs='?',
            default=10000,
            help='Ratio (default: 10000)'
        )

    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()
        
        with transaction.atomic():
            self.stdout.write('Clearing existing data...')
            QuestionLike.objects.all().delete()
            AnswerLike.objects.all().delete()
            Answer.objects.all().delete()
            Question.tags.through.objects.all().delete()
            Question.objects.all().delete()
            Tag.objects.all().delete()
            Profile.objects.exclude(user__is_superuser=True).delete()
            User.objects.exclude(is_superuser=True).delete()

            self.stdout.write('Generating users and profiles...')
            users = [
                User(
                    username=fake.user_name() + str(random.randint(1, 99999)),
                    email=fake.email(),
                    password='password123'
                )
                for _ in range(ratio)
            ]
            users = User.objects.bulk_create(users, batch_size=self.BATCH_SIZE)

            avatar_path = Path('static/img/cat.jpg')
            profiles = []
            with open(avatar_path, 'rb') as avatar_file:
                for user in users:
                    profile = Profile(
                        user=user,
                        nickname=fake.user_name()
                    )
                    profile.avatar.save(
                        f'cat_{user.id}.jpg',
                        File(avatar_file),
                        save=False
                    )
                    profiles.append(profile)
                    avatar_file.seek(0)
            
            Profile.objects.bulk_create(profiles, batch_size=self.BATCH_SIZE)

            self.stdout.write('Generating tags...')
            tags = [
                Tag(name=fake.word() + str(random.randint(1, 99999)))
                for _ in range(ratio)
            ]
            tags = Tag.objects.bulk_create(tags, batch_size=self.BATCH_SIZE)

            self.stdout.write('Generating questions...')
            questions = [
                Question(
                    title=fake.sentence(),
                    content=fake.text(),
                    author=random.choice(users),
                    created_at=fake.date_time_between(
                        start_date='-1y',
                        end_date='now',
                        tzinfo=timezone.get_current_timezone()
                    )
                )
                for _ in range(ratio * 10)
            ]
            questions = Question.objects.bulk_create(questions, batch_size=self.BATCH_SIZE)

            question_tags = []
            for question in questions:
                for tag in random.sample(tags, k=random.randint(1, 3)):
                    question_tags.append(
                        Question.tags.through(question_id=question.id, tag_id=tag.id)
                    )
            Question.tags.through.objects.bulk_create(
                question_tags, 
                batch_size=self.BATCH_SIZE,
                ignore_conflicts=True
            )

            question_answers_count = {q.id: 0 for q in questions}
            
            self.stdout.write('Generating answers...')
            answers = []
            for _ in range(ratio * 100):
                question = random.choice(questions)
                answers.append(
                    Answer(
                        content=fake.text(),
                        question=question,
                        is_correct=random.choice([True, False]),
                        author=random.choice(users),
                        created_at=fake.date_time_between(
                            start_date='-1y',
                            end_date='now',
                            tzinfo=timezone.get_current_timezone()
                        )
                    )
                )
                question_answers_count[question.id] += 1
            
            answers = Answer.objects.bulk_create(answers, batch_size=self.BATCH_SIZE)

            Question.objects.bulk_update([
                Question(id=q_id, answers_count=count)
                for q_id, count in question_answers_count.items()
            ], ['answers_count'], batch_size=self.BATCH_SIZE)

            question_likes_count = {q.id: 0 for q in questions}
            answer_likes_count = {a.id: 0 for a in answers}

            self.stdout.write('Generating likes...')
            question_likes = []
            for _ in range(ratio * 100):
                question = random.choice(questions)
                like_type = random.choice(['like', 'dislike'])
                question_likes.append(
                    QuestionLike(
                        author=random.choice(users),
                        question=question,
                        type=like_type
                    )
                )
                question_likes_count[question.id] += 1 if like_type == 'like' else -1

            QuestionLike.objects.bulk_create(
                question_likes, 
                batch_size=self.BATCH_SIZE,
                ignore_conflicts=True
            )

            answer_likes = []
            for _ in range(ratio * 100):
                answer = random.choice(answers)
                like_type = random.choice(['like', 'dislike'])
                answer_likes.append(
                    AnswerLike(
                        author=random.choice(users),
                        answer=answer,
                        type=like_type
                    )
                )
                answer_likes_count[answer.id] += 1 if like_type == 'like' else -1

            AnswerLike.objects.bulk_create(
                answer_likes, 
                batch_size=self.BATCH_SIZE,
                ignore_conflicts=True
            )

            Question.objects.bulk_update([
                Question(id=q_id, rating=count)
                for q_id, count in question_likes_count.items()
            ], ['rating'], batch_size=self.BATCH_SIZE)

            Answer.objects.bulk_update([
                Answer(id=a_id, rating=count)
                for a_id, count in answer_likes_count.items()
            ], ['rating'], batch_size=self.BATCH_SIZE)

        self.stdout.write(self.style.SUCCESS('Successfully filled database'))
