from django.contrib import admin

from .models import Question, Answer, Tag, Profile, QuestionLike, AnswerLike

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(Profile)
admin.site.register(QuestionLike)
admin.site.register(AnswerLike)