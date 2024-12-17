from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count

class ProfileManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('user')
        return queryset
    
    def get_top_profiles_by_rating(self):
        return self.get_queryset().annotate(
            rating=models.Sum('user__questions__rating') + models.Sum('user__answers__rating')
        ).order_by('-rating')[:5]
    
    def by_id(self, profile_id):
        return self.get_queryset().filter(id=profile_id)
    
class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='images/', null=True, blank=True)
    nickname = models.CharField(max_length=255, unique=False)

    objects = ProfileManager()

    def __str__(self):
        return self.user.username
    
class TagManager(models.Manager):
    def top_tags_by_questions_count(self):
        return self.get_queryset().annotate(questions_count=models.Count('questions')).order_by('-questions_count')[:5]

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    objects = TagManager()

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

class QuestionManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('author').prefetch_related('tags')
        return queryset

    def new(self):
        return self.get_queryset().order_by('-created_at')

    def hot(self):
        return self.get_queryset().order_by('-rating', '-created_at')
    
    def by_tag(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name).order_by('-created_at')

    def by_id(self, question_id):
        return self.get_queryset().filter(id=question_id)

class Question(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    tags = models.ManyToManyField(Tag, related_name='questions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    likes = models.ManyToManyField(User, through='QuestionLike', related_name='liked_questions_set')
    rating = models.IntegerField(default=0)
    answers_count = models.IntegerField(default=0)

    objects = QuestionManager()

    def __str__(self):
        return self.title
    
    def has_liked(self, user):
        return self.likes.filter(id=user).exists()

    class Meta:
        indexes = [
            models.Index(fields=['-created_at'], name='question_created_at_idx'),
            models.Index(fields=['-rating', '-created_at'], name='question_hot_idx'),
        ]

class AnswerManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('author')
        return queryset

    def correct(self):
        return self.get_queryset().filter(is_correct=True)
    
    def old(self):
        return self.get_queryset().order_by('created_at')
    
    def by_id(self, answer_id):
        return self.get_queryset().filter(id=answer_id)

    def by_question(self, question_id):
        return self.get_queryset().filter(question_id=question_id).order_by('created_at')

class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    likes = models.ManyToManyField(User, through='AnswerLike', related_name='liked_answers_set')
    rating = models.IntegerField(default=0)

    objects = AnswerManager()

    def __str__(self):
        return self.content
    
    def has_liked(self, user):
        return self.likes.filter(id=user).exists()
    
    def save(self, *args, **kwargs):
        Question.objects.filter(pk=self.question_id).update(
            answers_count=models.F('answers_count') + 1
        )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        question_id = self.question_id
        result = super().delete(*args, **kwargs)
        Question.objects.filter(pk=question_id).update(
            answers_count=models.F('answers_count') - 1
        )
        return result

    class Meta:
        indexes = [
            models.Index(fields=['-created_at'], name='answer_created_at_idx'),
            models.Index(fields=['created_at'], name='answer_created_at_asc_idx'),
        ]

class QuestionLike(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=10, choices=[('like', 'like'), ('dislike', 'dislike')])
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_likes')

    class Meta:
        unique_together = ['question', 'author']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            if self.type == 'like':
                Question.objects.filter(pk=self.question_id).update(
                    rating=models.F('rating') + 1
                )   
            else:
                Question.objects.filter(pk=self.question_id).update(
                    rating=models.F('rating') - 1
                )

    def delete(self, *args, **kwargs):
        if self.type == 'like': 
            Question.objects.filter(pk=self.question_id).update(
                rating=models.F('rating') - 1
            )
        else:
            Question.objects.filter(pk=self.question_id).update(
                rating=models.F('rating') + 1
            )
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.author.username} liked {self.question.title[:10]}..."

class AnswerLike(models.Model):
    id = models.AutoField(primary_key=True)  
    type = models.CharField(max_length=10, choices=[('like', 'like'), ('dislike', 'dislike')])
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_likes')

    class Meta:
        unique_together = ['answer', 'author']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            if self.type == 'like': 
                Answer.objects.filter(pk=self.answer_id).update(
                    rating=models.F('rating') + 1
                )
            else:
                Answer.objects.filter(pk=self.answer_id).update(
                    rating=models.F('rating') - 1
                )
    
    def delete(self, *args, **kwargs):
        if self.type == 'like':
            Answer.objects.filter(pk=self.answer_id).update(
                rating=models.F('rating') - 1
            )
        else:
            Answer.objects.filter(pk=self.answer_id).update(
                rating=models.F('rating') + 1
            )
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.author.username} liked {self.answer.content[:10]}..."