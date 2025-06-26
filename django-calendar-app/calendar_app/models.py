from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Note(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Person(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='people')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Event(models.Model):
    TAG_CHOICES = [
        ('meet', 'Meet'),
        ('reminder', 'Reminder'),
        ('event', 'Event'),
    ]
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    person = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True, blank=True)
    manual_name = models.CharField(max_length=100, blank=True)
    manual_surname = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    tag = models.CharField(max_length=20, choices=TAG_CHOICES)
    note = models.TextField(blank=True)

    def __str__(self):
        if self.person:
            return f"{self.person} - {self.date} ({self.tag})"
        return f"{self.manual_name} {self.manual_surname} - {self.date} ({self.tag})"