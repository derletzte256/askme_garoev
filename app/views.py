from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import auth

from .models import Question, Answer, Profile, Tag, QuestionLike, AnswerLike
from .forms import LoginForm, SignupForm, AskForm, AnswerForm, ProfileEditForm
from django.shortcuts import get_object_or_404
from django.conf import settings
import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def get_top_profiles_and_tags():
    top_profiles = Profile.objects.get_top_profiles_by_rating()
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

def get_paginated_questions(request, questions):
    questions, page_data = paginate(questions, request, 5)
    
    if request.user.is_authenticated:
        user_id = request.user.id
        for question in questions:
            question.has_voted = any(like.id == user_id for like in question.likes.all())
    else:
        for question in questions:
            question.has_voted = False
    
    top_profiles, top_tags = get_top_profiles_and_tags()
    return {
        'questions': questions,
        'page_data': page_data,
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'user': request.user,
    }

def get_paginated_answers(request, answers):
    answers, page_data = paginate(answers, request, 5)
    if request.user.is_authenticated:
        user_id = request.user.id
        for answer in answers:
            answer.has_voted = answer.has_liked(user_id)
    else:
        for answer in answers:
            answer.has_voted = False
    return answers, page_data

def get_paginated_questions(request, questions):
    questions, page_data = paginate(questions, request, 5)
    if request.user.is_authenticated:
        user_id = request.user.id
        for question in questions:
            question.has_voted = question.has_liked(user_id)
    else:
        for question in questions:
            question.has_voted = False
    top_profiles, top_tags = get_top_profiles_and_tags()
    return {
        'questions': questions,
        'page_data': page_data,
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'user': request.user,
    }

def index(request):
    all_questions = Question.objects.new()
    context = get_paginated_questions(request, all_questions)
    return render(request, 'index.html', context=context)


def hot(request):
    all_questions = Question.objects.hot()
    context = get_paginated_questions(request, all_questions)
    return render(request, 'hot.html', context=context)


def handle_answer_form(request, question_id, form):
    if request.method == 'POST' and form.is_valid() and request.user:
        answer_id = form.save()
        answers, page_data = paginate(Answer.objects.by_question(question_id), request, 5)
        last_page = page_data['pages']
        return redirect(f'/question/{question_id}/?page={last_page}#answer_{answer_id}')

    return None


def question(request, question_id):
    form = AnswerForm(request.POST or None, user=request.user, question=question_id)
    redirect_response = handle_answer_form(request, question_id, form)
    if redirect_response:
        return redirect_response

    top_profiles, top_tags = get_top_profiles_and_tags()
    question = get_object_or_404(Question.objects.by_id(question_id))
    all_answers = Answer.objects.by_question(question_id)
    answers, page_data = get_paginated_answers(request, all_answers)
    context = {
        'question': question,
        'answers': answers,
        'page_data': page_data,
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'user': request.user,
        'form': form,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'question.html', context=context)


def handle_ask_form(request, form):
    if request.method == 'POST' and form.is_valid():
        question_id = form.save()
        return redirect('question', question_id=question_id)
    return None


@login_required(login_url='/login/')
def ask(request):
    top_profiles, top_tags = get_top_profiles_and_tags()
    form = AskForm(request.POST or None, user=request.user)
    redirect_response = handle_ask_form(request, form)
    if redirect_response:
        return redirect_response

    context = {
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'form': form,
        'user': request.user
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
        'top_tags': top_tags,
        'user': request.user
    }
    return render(request, 'tag.html', context=context)


def handle_login_form(request, form):
    if request.method == 'POST' and form.is_valid():
        user = auth.authenticate(
            request, 
            username=form.cleaned_data['username'], 
            password=form.cleaned_data['password']
        )
        if user:
            auth.login(request, user)
            try:
                if request.POST.get('next'):
                    return redirect(request.POST.get('next'))
                return redirect('index')
            except Exception as e:
                return redirect('index')
        else:
            form.add_error(None, "Invalid username or password")
    return None


def login(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = LoginForm(request.POST or None)
    redirect_response = handle_login_form(request, form)
    if redirect_response:
        return redirect_response

    top_profiles, top_tags = get_top_profiles_and_tags()
    context = {
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'form': form,
        'user': request.user
    }
    return render(request, 'login.html', context=context)


def logout(request):
    auth.logout(request)
    return redirect('index')


def handle_signup_form(request, form):
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        print(user)
        return redirect('index')
    return None


def signup(request):
    top_profiles, top_tags = get_top_profiles_and_tags()
    form = SignupForm(request.POST or None, request.FILES or None)
    redirect_response = handle_signup_form(request, form)
    if redirect_response:
        return redirect_response

    context = {
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'form': form,
        'user': request.user
    }
    return render(request, 'signup.html', context=context)


def handle_profile_edit_form(request, form):
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('profile.edit')
    return None


def profile_edit(request):
    top_profiles, top_tags = get_top_profiles_and_tags()
    form = ProfileEditForm(request.POST or None, request.FILES or None, user=request.user)
    redirect_response = handle_profile_edit_form(request, form)
    if redirect_response:
        return redirect_response

    context = {
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'form': form,
        'user': request.user,
        'MEDIA_URL': settings.MEDIA_URL
    }
    return render(request, 'profile_edit.html', context=context)


def page_not_found(request, exception):
    top_profiles, top_tags = get_top_profiles_and_tags()
    context = {
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'user': request.user
    }
    return render(request, '404.html', context=context)


def profile(request, profile_id):
    top_profiles, top_tags = get_top_profiles_and_tags()
    profile_model = get_object_or_404(Profile.objects.by_id(profile_id))
    context = {
        'profile': profile_model,
        'top_profiles': top_profiles,
        'top_tags': top_tags,
        'user': request.user,
        'MEDIA_URL': settings.MEDIA_URL
    }
    return render(request, 'profile.html', context=context)

@require_POST
@login_required(login_url='/login/')
def like_question(request):
    body = json.loads(request.body)
    like_type = body.get('type')
    question_id = body.get('question_id')
    question = Question.objects.by_id(question_id).first()
    if not question:
        return JsonResponse({'status': 'error', 'message': 'Question not found'}, status=404)
    if like_type == 'like':
        like = QuestionLike.objects.create(question=question, author=request.user, type='like')
        like.save()
    elif like_type == 'dislike':
        like = QuestionLike.objects.create(question=question, author=request.user, type='dislike')
        like.save()
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid like type'}, status=400)
    question = Question.objects.by_id(question_id).first()
    if not question:
        return JsonResponse({'status': 'error', 'message': 'Question not found'}, status=404)
    current_rating = question.rating
    return JsonResponse({'status': 'success', 'rating': current_rating})

@require_POST
@login_required(login_url='/login/')
def like_answer(request):
    body = json.loads(request.body)
    like_type = body.get('type')
    answer_id = body.get('answer_id')
    answer = Answer.objects.by_id(answer_id).first()
    if not answer:
        return JsonResponse({'status': 'error', 'message': 'Answer not found'}, status=404)
    if like_type == 'like':
        like = AnswerLike.objects.create(answer=answer, author=request.user, type='like')
        like.save()
    elif like_type == 'dislike':
        like = AnswerLike.objects.create(answer=answer, author=request.user, type='dislike')
        like.save()
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid like type'}, status=400)
    answer = Answer.objects.by_id(answer_id).first()
    if not answer:
        print('Answer not found 2')
        return JsonResponse({'status': 'error', 'message': 'Answer not found'}, status=404)
    current_rating = answer.rating
    return JsonResponse({'status': 'success', 'rating': current_rating})

@require_POST
@login_required(login_url='/login/')
def approve_answer(request):
    body = json.loads(request.body)
    answer_id = body.get('answer_id')
    question_id = body.get('question_id')
    answer = Answer.objects.by_id(answer_id).first()
    question = Question.objects.by_id(question_id).first()
    if not answer or not question:
        return JsonResponse({'status': 'error', 'message': 'Answer or question not found'}, status=404)
    if request.user != question.author:
        return JsonResponse({'status': 'error', 'message': 'Only question author can approve answers'}, status=403)
    answer.is_correct = not answer.is_correct
    answer.save()
    return JsonResponse({'status': 'success', 'is_correct': answer.is_correct})



