from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Client(models.Model):
    first_name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name}"
    
    @receiver(post_save, sender=User)
    def create_default_tags(sender, instance, created, **kwargs):
        if created:
            EventTag.objects.create(client=instance, name='Susitikimas', color='#1976d2', is_default=True)
            EventTag.objects.create(client=instance, name='Priminimas', color='#43a047', is_default=True)
            EventTag.objects.create(client=instance, name='Skambutis', color='#fbc02d', is_default=True)

            PersonRole.objects.create(client=instance, name='Būsimas', color='#607d8b', is_default=True)
            PersonRole.objects.create(client=instance, name='Naujas', color='#43a047', is_default=True)
            PersonRole.objects.create(client=instance, name='Derinama', color='#fbc02d', is_default=True)

    
class Person(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='people')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    role = models.ForeignKey('PersonRole', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class EventTag(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_tags', null=True, blank=True)
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=7, default='#1976d2')

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Event(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    person = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True, blank=True)
    manual_name = models.CharField(max_length=100, blank=True)
    manual_surname = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    tag = models.ForeignKey(EventTag, on_delete=models.CASCADE)

    note = models.TextField(blank=True)

    def __str__(self):
        if self.person:
            return f"{self.person} - {self.date} ({self.tag})"
        return f"{self.manual_name} {self.manual_surname} - {self.date} ({self.tag})"
    

class PersonRole(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='person_roles')
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=7, default='#607d8b')
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name