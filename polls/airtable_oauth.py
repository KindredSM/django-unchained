from requests_oauthlib import OAuth2Session
from django.conf import settings
from django.urls import reverse


def get_airtable_auth_url(request):
    oauth = OAuth2Session(
        settings.AIRTABLE_CLIENT_ID,
        redirect_uri=request.build_absolute_uri(reverse('polls:airtable_callback')),
        scope=['data.records:read', 'data.records:write']
    )
    authorization_url, state = oauth.authorization_url('https://airtable.com/oauth2/v1/authorize')
    request.session['oauth_state'] = state
    return authorization_url

def get_airtable_token(request):
    oauth = OAuth2Session(
        settings.AIRTABLE_CLIENT_ID,
        state=request.session['oauth_state'],
        redirect_uri=request.build_absolute_uri(reverse('polls:airtable_callback'))
    )
    token = oauth.fetch_token(
        'https://airtable.com/oauth2/v1/token',
        client_secret=settings.AIRTABLE_CLIENT_SECRET,
        authorization_response=request.build_absolute_uri()
    )
    return token