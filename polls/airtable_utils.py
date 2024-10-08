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
                'Date Published': question.pub_date.isoformat()
            }
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            print(f"Failed to create record for question {question.id}: {response.text}")
        else:
            print(f"Successfully synced question {question.id} to Airtable")

def sync_questions_from_airtable(request):
    access_token = get_airtable_client(request)
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    url = f'https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_TABLE_NAME}'
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch records from Airtable: {response.text}")
    
    data = response.json()
    records = data.get('records', [])
    for record in records:
        fields = record['fields']
        question_text = fields.get('Question')
        pub_date = fields.get('Date Published')
        if question_text and pub_date:
            Question.objects.update_or_create(
                question_text=question_text,
                defaults={'pub_date': pub_date}
            )
    return len(records)