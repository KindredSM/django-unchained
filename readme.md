# Django Polls

built with Django 3.2.23 and Python 3.8.13.

## Features

- Create and manage polls
- Vote on polls
- View poll results

## Prerequisites

- Python 3.8.13
- PostgreSQL

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/django-polls-app.git
   cd django-polls-app
   ```

2. Create a virtual environment and activate it:

   ```
   python3.8 -m venv env
   source env/bin/activate
   ```

3. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your PostgreSQL database credentials:

   ```
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. Run migrations:

   ```
   python manage.py migrate
   ```

6. Create a superuser:

   ```
   python manage.py createsuperuser
   ```

7. Run the development server:

   ```
   python manage.py runserver
   ```

8. Visit `http://127.0.0.1:8000/admin/` to access the admin interface and start creating polls.
