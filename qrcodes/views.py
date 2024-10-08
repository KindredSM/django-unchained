from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from polls.models import QRCode, Question
from polls.forms import QRCodeForm
from django.contrib.auth.decorators import login_required
from polls.airtable_utils import sync_qrcodes_to_airtable, sync_qrcodes_from_airtable
from polls.airtable_oauth import get_airtable_auth_url, get_airtable_token
from django.conf import settings
from requests_oauthlib import OAuth2Session
from django.urls import reverse
from django.http import HttpResponseRedirect
from requests.auth import HTTPBasicAuth
import os
import hashlib
import base64
import secrets
from django.contrib import messages

def index(request):
    qr_codes = QRCode.objects.order_by('-creation_date')
    context = {'qr_codes': qr_codes}
    return render(request, 'qrcodes/index.html', context)

def detail(request, qr_code_id):
    qr_code = get_object_or_404(QRCode, pk=qr_code_id)
    return render(request, 'qrcodes/detail.html', {'qr_code': qr_code})

def create_qrcode(request):
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            qr_code = form.save(commit=False)
            qr_code.creation_date = timezone.now()
            qr_code.save()
            return redirect('qrcodes:detail', qr_code_id=qr_code.id)
    else:
        form = QRCodeForm()
    return render(request, 'qrcodes/qrcode_form.html', {'form': form})

def update_qrcode(request, qr_code_id):
    qr_code = get_object_or_404(QRCode, pk=qr_code_id)
    if request.method == 'POST':
        form = QRCodeForm(request.POST, instance=qr_code)
        if form.is_valid():
            qr_code = form.save()
            return redirect('qrcodes:detail', qr_code_id=qr_code.id)
    else:
        form = QRCodeForm(instance=qr_code)
    return render(request, 'qrcodes/qrcode_form.html', {'form': form})

def delete_qrcode(request, qr_code_id):
    qr_code = get_object_or_404(QRCode, pk=qr_code_id)
    if request.method == 'POST':
        qr_code.delete()
        return redirect('qrcodes:index')
    return render(request, 'qrcodes/qrcode_confirm_delete.html', {'qr_code': qr_code})

@login_required
def sync_to_airtable(request):
    try:
        sync_qrcodes_to_airtable(request)
        messages.success(request, "Successfully synced QR codes to Airtable")
    except Exception as e:
        messages.error(request, f"Failed to sync to Airtable: {str(e)}")
    return redirect('qrcodes:index')

@login_required
def sync_from_airtable(request):
    try:
        synced_count = sync_qrcodes_from_airtable(request)
        messages.success(request, f"Successfully synced {synced_count} QR codes from Airtable")
    except Exception as e:
        messages.error(request, f"Failed to sync from Airtable: {str(e)}")
    return redirect('qrcodes:index')

def airtable_login(request):
    auth_url = get_airtable_auth_url(request)
    return redirect(auth_url)

def airtable_callback(request):
    try:
        token = get_airtable_token(request)
        request.session['airtable_token'] = token
        return redirect('qrcodes:index')
    except Exception as e:
        return render(request, 'qrcodes/error.html', {'error': str(e)})

@login_required
def initiate_airtable_oauth(request):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development with ngrok
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
    token = oauth.fetch_token(
        settings.AIRTABLE_TOKEN_URL,
        authorization_response=request.build_absolute_uri(),
        code_verifier=code_verifier,
        client_secret=settings.AIRTABLE_CLIENT_SECRET
    )
    request.session['airtable_token'] = token
    return redirect('qrcodes:index')

@login_required
def airtable_disconnect(request):
    if 'airtable_token' in request.session:
        del request.session['airtable_token']
    return redirect('qrcodes:index')