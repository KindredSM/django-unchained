from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:question_id>/', views.detail, name='detail'),
    path('create/', views.create_question, name='create_question'),
    path('<int:question_id>/update/', views.update_question, name='update_question'),
    path('<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('<int:question_id>/add_choice/', views.add_choice, name='add_choice'),
    path('sync-to-airtable/', views.sync_to_airtable, name='sync_to_airtable'),
    path('sync-from-airtable/', views.sync_from_airtable, name='sync_from_airtable'),
    path('airtable-login/', views.airtable_login, name='airtable_login'),
    path('airtable-callback/', views.airtable_callback, name='airtable_callback'),
]