import requests
from django.conf import settings
from .models import Question

def get_airtable_client(request):
    token = request.session.get('airtable_token')
    if not token:
        raise Exception("Airtable token not found. Please authenticate first.")
    return token['access_token']

def sync_questions_to_airtable(request):
    access_token = get_airtable_client(request)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    url = f'https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_TABLE_NAME}'
    
    questions = Question.objects.all()
    for question in questions:
        data = {
            'fields': {
                'Question': question.question_text,
                'Date Published': str(question.pub_date)
            }
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

def sync_questions_from_airtable(request):
    access_token = get_airtable_client(request)
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    url = f'https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_TABLE_NAME}'
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    records = response.json()['records']
    
    for record in records:
        Question.objects.get_or_create(
            question_text=record['fields']['Question'],
            pub_date=record['fields']['Date Published']
        )