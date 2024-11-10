import copy

from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.shortcuts import render

from random import randint

TAGS = ('blender', 'black jack')
ANSWERS = [
    {
        'title': f'Answer {i}',
        'text': f'This is the text for answer {i}',
        'rating': 1 + (i % 7),
        'is_correct': False
    } for i in range(1, 20)
]

QUESTIONS = [
    {
        'title': f'Question {i}',
        'text': f'This is the text for question {i}',
        'id': i,
        'tags': TAGS,
        'answers': ANSWERS,
        'answers_len': len(ANSWERS),
        'rating': 1 + (i % 7)
    } for i in range(1, 20)
]


def paginate(objects_list, request, per_page=10):
    # use Paginator
    # Also add somthing to PageNotAnInteger and EmptyPage

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

    return page_obj.object_list, page_obj


def index(request):
    questions, page = paginate(QUESTIONS, request, 5)
    return render(request, 'index.html', context={'questions': questions, 'page_obj': page})


def hot(request):
    hot_questions = copy.deepcopy(QUESTIONS)
    hot_questions.reverse()
    hot_questions, page = paginate(hot_questions, request, 5)
    return render(request, 'hot.html', context={'questions': hot_questions, 'page_obj': page})


def question(request, question_id):
    one_question = QUESTIONS[question_id - 1]
    answers, page = paginate(one_question['answers'], request, 5)
    return render(request, 'question.html', context={'question': one_question, 'answers': answers, 'page_obj': page})


def ask(request):
    return render(request, 'ask.html')


def tag(request, tag_name):
    tag_questions = [question for question in QUESTIONS if tag_name in question['tags']]
    tag_questions, page = paginate(tag_questions, request, 5)
    return render(request, 'tag.html', context={'questions': tag_questions, 'tag': tag_name, 'page_obj': page})


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'signup.html')


def settings(request):
    return render(request, 'settings.html')
