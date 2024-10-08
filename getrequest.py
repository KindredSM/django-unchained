import os
import django
import requests

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.conf import settings

print("Script is running")

def check_airtable_connection():
    base_id = settings.AIRTABLE_BASE_ID
    table_name = settings.AIRTABLE_QUESTIONS_TABLE
    
    # You need to implement a function to get the access token
    access_token = get_access_token()

    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tables = response.json().get('tables', [])
        for table in tables:
            if table['name'] == table_name:
                print(f"Found table: {table_name}")
                return
        print(f"Table {table_name} not found in base")
    else:
        print(f"Error accessing Airtable API: {response.status_code} - {response.text}")

def get_access_token():
    # Implement your OAuth flow here to get the access token
    # This might involve checking if you have a valid token stored,
    # and if not, going through the OAuth flow to get a new one
    pass

# Call the function
check_airtable_connection()

print("Script has finished")