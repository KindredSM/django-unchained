from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    question_text = models.CharField(max_length=200, null=False, blank=False)
    pub_date = models.DateTimeField('date published', null=True, blank=True)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


class AirtableToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=5000)
    refresh_token = models.CharField(max_length=5000)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return self.expires_at <= timezone.now()
