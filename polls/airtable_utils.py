import requests
from django.conf import settings
from .models import Question, Choice, AirtableToken
from django.utils.dateparse import parse_datetime

def get_airtable_headers(request):
    user = request.user
    try:
        token = AirtableToken.objects.get(user=user)
        if token.is_expired():
            pass
        return {
            'Authorization': f"Bearer {token.access_token}",
            'Content-Type': 'application/json'
        }
    except AirtableToken.DoesNotExist:
        raise Exception("Airtable token not found. Please authenticate first.")

def sync_questions_to_airtable(request):
    headers = get_airtable_headers(request)
    questions_url = f"https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_QUESTIONS_TABLE}"

    for question in Question.objects.all():
        data = {
            "fields": {
                "Question Text": question.question_text,
            }
        }
        if question.pub_date:
            data["fields"]["Publication Date"] = question.pub_date.strftime("%Y-%m-%d")
        
        response = requests.post(questions_url, json=data, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to sync question: {response.text}")

def sync_questions_from_airtable(request):
    headers = get_airtable_headers(request)
    questions_url = f"https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_QUESTIONS_TABLE}"
    
    response = requests.get(questions_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch questions: {response.text}")
    
    data = response.json()
    for record in data.get('records', []):
        question_text = record['fields'].get('Question Text')
        pub_date_str = record['fields'].get('Publication Date')
        if question_text:
            pub_date = parse_datetime(pub_date_str) if pub_date_str else None
            Question.objects.update_or_create(
                question_text=question_text,
                defaults={'pub_date': pub_date}
            )
        else:
            print(f"Skipping record with empty question text: {record}")

def sync_questions_from_airtable(request):
    headers = get_airtable_headers(request)
    questions_url = f"https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_QUESTIONS_TABLE}"

    response = requests.get(questions_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch questions: {response.text}")

    questions_data = response.json().get('records', [])
    for question_record in questions_data:
        question_text = question_record['fields'].get('Question Text')
        choices_text = question_record['fields'].get('Choices', '')

        question, created = Question.objects.update_or_create(
            question_text=question_text,

        )

        # Clear existing choices and create new ones
        question.choice_set.all().delete()
        for choice_text in choices_text.split(','):
            Choice.objects.create(question=question, choice_text=choice_text.strip())