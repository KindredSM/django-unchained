from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Question, Choice
from .forms import QuestionForm, ChoiceForm
from django.contrib.auth.decorators import login_required
from .airtable_utils import sync_questions_to_airtable, sync_questions_from_airtable
from .airtable_oauth import get_airtable_auth_url, get_airtable_token
from django.conf import settings

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.pub_date = timezone.now()
            question.save()
            return redirect('polls:detail', question_id=question.id)
    else:
        form = QuestionForm()
    return render(request, 'polls/question_form.html', {'form': form})

def update_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.pub_date = timezone.now()
            question.save()
            return redirect('polls:detail', question_id=question.id)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'polls/question_form.html', {'form': form})

def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        question.delete()
        return redirect('polls:index')
    return render(request, 'polls/question_confirm_delete.html', {'question': question})

def add_choice(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            return redirect('polls:detail', question_id=question.id)
    else:
        form = ChoiceForm()
    return render(request, 'polls/choice_form.html', {'form': form, 'question': question})

@login_required
def sync_to_airtable(request):
    sync_questions_to_airtable(request)
    return redirect('polls:index')

@login_required
def sync_from_airtable(request):
    sync_questions_from_airtable(request)
    return redirect('polls:index')

def airtable_login(request):
    auth_url = get_airtable_auth_url(request)
    return redirect(auth_url)

def airtable_callback(request):
    try:
        token = get_airtable_token(request)
        request.session['airtable_token'] = token
        return redirect('polls:index')
    except Exception as e:
        return render(request, 'polls/error.html', {'error': str(e)})