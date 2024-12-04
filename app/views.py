import copy

from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.contrib import auth

from .models import Question, Answer, Profile, Tag
from .forms import LoginForm, SignupForm, AskForm

from django.contrib.auth.decorators import login_required

def get_top_profiles_and_tags():
    top_profiles = Profile.objects.get_top_profiles_by_question_likes_count()
    top_tags = Tag.objects.top_tags_by_questions_count()
    return top_profiles, top_tags


def paginate(objects_list, request, per_page=10):
    page = request.GET.get('page')
    paginator = Paginator(objects_list, per_page)
    try:
        page_obj = paginator.get_page(page)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        if int(page) > paginator.num_pages:
            page_obj = paginator.get_page(paginator.num_pages)
        else:
            paginator.get_page(1)

    page_data = {
        'page': page_obj.number,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
    }

    return page_obj.object_list, page_data


def index(request):
    top_profiles, top_tags = get_top_profiles_and_tags()
    all_questions = Question.objects.new()
    questions, page_data = paginate(all_questions, request, 5)
    context = {
        'questions': questions,
        'page_data': page_data,
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'user': request.user
    }
    return render(request, 'index.html', context=context)


def hot(request):
    top_profiles, top_tags = get_top_profiles_and_tags()
    all_questions = Question.objects.hot()
    questions, page_data = paginate(all_questions, request, 5)
    context = {
        'questions': questions,
        'page_data': page_data,
        'top_profiles': top_profiles,
        'top_tags': top_tags
    }
    return render(request, 'hot.html', context=context)


def question(request, question_id):
    top_profiles, top_tags = get_top_profiles_and_tags()
    try:
        question = Question.objects.by_id(question_id)
    except Question.DoesNotExist:
        return page_not_found(request, "Question not found")   
    all_answers = Answer.objects.by_question(question_id)
    answers, page_data = paginate(all_answers, request, 5)
    context = {
        'question': question,
        'answers': answers,
        'page_data': page_data,
        'top_profiles': top_profiles,
        'top_tags': top_tags
    }
    return render(request, 'question.html', context=context)

@login_required(login_url='/login/')
def ask(request):
    top_profiles, top_tags = get_top_profiles_and_tags()
    form = AskForm(request.POST or None, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            question_id = form.save()
            return redirect('question', question_id=question_id)
    context = {
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'form': form
    }
    return render(request, 'ask.html', context=context)


def tag(request, tag_name):
    top_profiles, top_tags = get_top_profiles_and_tags()
    all_questions = Question.objects.by_tag(tag_name)
    if not all_questions:
        return page_not_found(request, "Tag not found")
    questions, page_data = paginate(all_questions, request, 5)
    context = {
        'questions': questions,
        'tag': tag_name,
        'page_data': page_data,
        'top_profiles': top_profiles,
        'top_tags': top_tags
    }
    return render(request, 'tag.html', context=context)



def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = LoginForm(request.POST or None)
    top_profiles, top_tags = get_top_profiles_and_tags()
    if request.method == 'POST':
        if form.is_valid():
            user = auth.authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                auth.login(request, user)
                return redirect('index')
            else:
                form.add_error(None, "Invalid username or password")
    context = {
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'form': form
    }
    return render(request, 'login.html', context=context)

def logout(request):
    auth.logout(request)
    return redirect('index')


def signup(request):
    top_profiles, top_tags = get_top_profiles_and_tags()
    form = SignupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.signup()
            print(user)
            return redirect('index')

    context = {
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'form': form
    }
    return render(request, 'signup.html', context=context)


def settings(request):
    top_profiles, top_tags = get_top_profiles_and_tags()
    context = {
        'top_profiles': top_profiles,
        'top_tags': top_tags
    }
    return render(request, 'settings.html', context=context)


def page_not_found(request, exception):
    top_profiles, top_tags = get_top_profiles_and_tags()
    context = {
        'top_profiles': top_profiles,
        'top_tags': top_tags
    }
    return render(request, '404.html', context=context)
