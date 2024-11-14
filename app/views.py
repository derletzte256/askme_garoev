import copy

from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.shortcuts import render

from .models import Question, Answer, Profile, Tag

def get_top_users_and_tags():
    top_users = Profile.objects.get_top_users_by_questions_count()
    top_tags = Tag.objects.top_tags_by_questions_count()
    return top_users, top_tags


def paginate(objects_list, request, per_page=10):
    page = request.GET.get('page')
    paginator = Paginator(objects_list, per_page,
                          error_messages={'invalid_page': 'Page not found',
                                          'min_page': 'Negative page number',
                                          'not_results': 'Empty page'}
                          )
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
    top_users, top_tags = get_top_users_and_tags()
    all_questions = Question.objects.new()
    questions, page_data = paginate(all_questions, request, 5)
    return render(request, 'index.html', context={'questions': questions, 'page_data': page_data, 'top_users': top_users, 'top_tags': top_tags})


def hot(request):
    top_users, top_tags = get_top_users_and_tags()
    all_questions = Question.objects.hot()
    questions, page_data = paginate(all_questions, request, 5)
    return render(request, 'hot.html', context={'questions': questions, 'page_data': page_data, 'top_users': top_users, 'top_tags': top_tags})


def question(request, question_id):
    top_users, top_tags = get_top_users_and_tags()
    try:
        question = Question.objects.by_id(question_id)
    except Question.DoesNotExist:
        return page_not_found(request, "Question not found")   
    all_answers = Answer.objects.by_question(question_id)
    answers, page_data = paginate(all_answers, request, 5)
    return render(request, 'question.html', context={'question': question, 'answers': answers, 'page_data': page_data, 'top_users': top_users, 'top_tags': top_tags})


def ask(request):
    top_users, top_tags = get_top_users_and_tags()
    return render(request, 'ask.html', context={'top_users': top_users, 'top_tags': top_tags})


def tag(request, tag_name):
    top_users, top_tags = get_top_users_and_tags()
    all_questions = Question.objects.by_tag(tag_name)
    if not all_questions:
        return page_not_found(request, "Tag not found")
    questions, page_data = paginate(all_questions, request, 5)
    return render(request, 'tag.html', context={'questions': questions, 'tag': tag_name, 'page_data': page_data, 'top_users': top_users, 'top_tags': top_tags})


def login(request):
    top_users, top_tags = get_top_users_and_tags()
    return render(request, 'login.html', context={'top_users': top_users, 'top_tags': top_tags})


def signup(request):
    top_users, top_tags = get_top_users_and_tags()
    return render(request, 'signup.html', context={'top_users': top_users, 'top_tags': top_tags})


def settings(request):
    top_users, top_tags = get_top_users_and_tags()
    return render(request, 'settings.html', context={'top_users': top_users, 'top_tags': top_tags})


def page_not_found(request, exception):
    top_users, top_tags = get_top_users_and_tags()
    return render(request, '404.html', context={'top_users': top_users, 'top_tags': top_tags})
