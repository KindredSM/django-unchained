from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import AirtableToken, Question, Choice
from .forms import QuestionForm, ChoiceForm
from django.contrib.auth.decorators import login_required
from .airtable_utils import sync_questions_to_airtable, sync_questions_from_airtable
from .airtable_oauth import get_airtable_auth_url, get_airtable_token
from django.conf import settings
from requests_oauthlib import OAuth2Session
import os
import hashlib
import base64
import secrets
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

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
    try:
        sync_questions_to_airtable(request)
        messages.success(request, "Successfully synced questions to Airtable.")
    except Exception as e:
        logger.error(f"Error syncing to Airtable: {str(e)}")
        messages.error(request, f"Error syncing to Airtable: {str(e)}")
    return redirect('polls:index')

@login_required
def sync_from_airtable(request):
    try:
        sync_questions_from_airtable(request)
        messages.success(request, "Successfully synced questions from Airtable.")
    except Exception as e:
        logger.error(f"Error syncing from Airtable: {str(e)}")
        messages.error(request, f"Error syncing from Airtable: {str(e)}")
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

@login_required
def initiate_airtable_oauth(request):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # only for dev with ngrok
    code_verifier = secrets.token_urlsafe(128)[:128]
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).decode('utf-8').rstrip('=')
    
    oauth = OAuth2Session(
        settings.AIRTABLE_CLIENT_ID,
        redirect_uri=settings.AIRTABLE_REDIRECT_URI,
        scope=settings.AIRTABLE_SCOPES
    )
    authorization_url, state = oauth.authorization_url(
        settings.AIRTABLE_AUTH_URL,
        code_challenge=code_challenge,
        code_challenge_method='S256'
    )
    request.session['oauth_state'] = state
    request.session['code_verifier'] = code_verifier
    return redirect(authorization_url)

@login_required
def airtable_oauth_callback(request):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # only for deve with ngrok
    oauth = OAuth2Session(
        settings.AIRTABLE_CLIENT_ID,
        redirect_uri=settings.AIRTABLE_REDIRECT_URI,
        state=request.session.get('oauth_state')
    )
    code_verifier = request.session.get('code_verifier')
    token_response = oauth.fetch_token(
        settings.AIRTABLE_TOKEN_URL,
        authorization_response=request.build_absolute_uri(),
        code_verifier=code_verifier,
        client_secret=settings.AIRTABLE_CLIENT_SECRET
    )
    user = request.user
    expires_in = token_response.get('expires_in', 7200) 
    expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
    
    AirtableToken.objects.update_or_create(
        user=user,
        defaults={
            'access_token': token_response['access_token'],
            'refresh_token': token_response.get('refresh_token', ''),
            'expires_at': expires_at
        }
    )
    request.session['airtable_token'] = token_response['access_token']
    return redirect('polls:index')

@login_required
def airtable_disconnect(request):
    if 'airtable_token' in request.session:
        del request.session['airtable_token']
    return redirect('polls:index')