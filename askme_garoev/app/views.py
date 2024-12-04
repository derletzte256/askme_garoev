import copy

from django.http import HttpResponse
from django.shortcuts import render

QUESTIONS = [
    {
        'title' : 'Title' + str(i),
        'id': i,
        'text': 'This is text for question #' + str(i)
    } for i in range(1, 5)
]


# Create your views here.
def index(request):
    return render(request, 'index.html', context={'questions': QUESTIONS})

def hot(request):
    hot_questions = copy.deepcopy(QUESTIONS)
    hot_questions.reverse()
    return render(request, 'hot.html', context={'questions': hot_questions})

def question(request, question_id):
    one_question = QUESTIONS[question_id]
    return render(request, 'question.html', context={'question': question})


