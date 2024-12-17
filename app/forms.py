from django import forms
from django.contrib.auth.models import User
from app.models import Profile, Question, Tag, Answer

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-50'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control w-50'}))
    confirm = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def clean_username(self):
        return self.cleaned_data['username'].lower().strip()
    
    def clean_password(self):
        return self.cleaned_data['password'].strip()


class SignupForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-50'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control w-50'}))
    nickname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-50'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control w-50'}))
    repeat_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control w-50'}))
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control w-50'}), required=True)

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError('Username already exists')
        return self.cleaned_data['username'].lower().strip()
    
    def clean_nickname(self):
        return self.cleaned_data['nickname'].lower().strip()
    
    def clean_password(self):
        return self.cleaned_data['password'].strip()
    
    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError('Email already exists')
        return self.cleaned_data['email'].lower().strip()
    
    def clean_repeat_password(self):
        return self.cleaned_data['repeat_password'].strip()
    
    def clean(self):
        data = super().clean()
        if data['password'] != data['repeat_password']:
            raise forms.ValidationError('Passwords do not match')
        
    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'], 
            password=self.cleaned_data['password']
        )   
        user.save()     

        profile = Profile.objects.create(
            user=user,
            nickname=self.cleaned_data['nickname'],
            avatar=self.cleaned_data['avatar']
        )
        profile.save()

        return user
    
class AskForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-100'}), label='Title', max_length=255)
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control w-100'}), label='Text', max_length=2048)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-100'}), label='Tags', max_length=255, required=False)

    def clean_tags(self):
        _tags = self.cleaned_data['tags'].split(' ') if self.cleaned_data['tags'] else []
        if len(_tags) > 3:
            raise forms.ValidationError('Too many tags (maximum 3)')
        
        return _tags
    def save(self):
        question = Question.objects.create(
            title=self.cleaned_data['title'],
            content=self.cleaned_data['text'],
            author=self.user
        )
        for tag in self.cleaned_data['tags']:
            tag, _ = Tag.objects.get_or_create(name=tag)
            question.tags.add(tag)

        question.save()

        return question.id
    

class AnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)

    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control w-100', 'rows': 3}), label='Text', max_length=2048)

    def save(self):
        question = Question.objects.by_id(self.question).first()
        answer = Answer.objects.create(
            content=self.cleaned_data['text'],
            author=self.user,
            question=question
        )

        answer.save()

        return answer.id


class ProfileEditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email
            self.fields['nickname'].initial = self.user.profile.nickname
            self.fields['avatar'].initial = self.user.profile.avatar

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-50'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control w-50'}))
    nickname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-50'}))
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control w-50'}), required=False)

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']).exclude(id=self.user.id).exists():
            raise forms.ValidationError('Username already exists')
        return self.cleaned_data['username'].lower().strip()
    
    def clean_nickname(self):
        return self.cleaned_data['nickname'].lower().strip()
    
    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exclude(id=self.user.id).exists():
            raise forms.ValidationError('Email already exists')
        return self.cleaned_data['email'].lower().strip()

    def save(self):
        user = User.objects.get(id=self.user.id)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.save()

        profile = user.profile
        profile.nickname = self.cleaned_data['nickname']
        profile.avatar = self.cleaned_data['avatar']
        profile.save()