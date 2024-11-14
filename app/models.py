from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count

class ProfileManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('user')
        return queryset
    
    def get_top_users_by_questions_count(self):
        users_ids = self.get_queryset().annotate(questions_count=Count('user__questions')).order_by('-questions_count')[:5].values_list('user', flat=True)
        return User.objects.filter(id__in=users_ids)
    
class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    objects = ProfileManager()

    def __str__(self):
        return self.user.username

class QuestionManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('author').prefetch_related('tags')
        return queryset

    def new(self):
        return self.get_queryset().order_by('-created_at')

    def hot(self):
        return self.get_queryset().order_by('-likes_count', '-created_at')
    
    def by_tag(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name).order_by('-created_at')

    def by_id(self, question_id):
        return self.get_queryset().get(id=question_id)
    
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

class Question(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    tags = models.ManyToManyField(Tag, related_name='questions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    likes = models.ManyToManyField(User, through='QuestionLike', related_name='liked_questions_set')
    likes_count = models.IntegerField(default=0)
    answers_count = models.IntegerField(default=0)

    objects = QuestionManager()

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['-created_at'], name='question_created_at_idx'),
            models.Index(fields=['-likes_count', '-created_at'], name='question_hot_idx'),
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

    def by_question(self, question_id):
        return self.get_queryset().filter(question_id=question_id)

class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    likes = models.ManyToManyField(User, through='AnswerLike', related_name='liked_answers_set')
    likes_count = models.IntegerField(default=0)

    objects = AnswerManager()

    def __str__(self):
        return self.content

    class Meta:
        indexes = [
            models.Index(fields=['-created_at'], name='answer_created_at_idx'),
            models.Index(fields=['created_at'], name='answer_created_at_asc_idx'),
        ]

class QuestionLike(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_likes')

    class Meta:
        unique_together = ['question', 'author']

    def __str__(self):
        return str(self.id)

class AnswerLike(models.Model):
    id = models.AutoField(primary_key=True)  
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_likes')

    class Meta:
        unique_together = ['answer', 'author']

    def __str__(self):
        return str(self.id)