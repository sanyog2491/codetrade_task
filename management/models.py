from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.utils import timezone
from django.db.models.signals import m2m_changed
from datetime import date
from django.core.exceptions import ValidationError


def validate_due_date(value):
    if value.date() < date.today():
        raise ValidationError("The due date cannot be in the past!")
    return value

class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=100, blank=True)
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_users = models.ManyToManyField(User, related_name='assigned_projects')
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=100, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='P')
    due_date = models.DateTimeField(validators=[validate_due_date])
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)  # Fix: use 'project' and set related_name here
    
    def __str__(self):
        return self.name


@receiver(m2m_changed, sender=Project.assigned_users.through)
def assigned_users_changed(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove']:
        users = kwargs.get('pk_set', [])
        user_list = User.objects.filter(pk__in=users)

        messages_list = []
        for user in user_list:
            if action == 'post_add':
                msg = f"{user.username} has been added to the project: {instance.name}."
            elif action == 'post_remove':
                msg = f"{user.username} has been removed from the project: {instance.name}."
            messages_list.append(msg)

        instance._messages_list = messages_list

@receiver(post_save, sender=Task)
def update_project_status(sender, instance, **kwargs):
    project = instance.project

    all_tasks_completed = project.tasks.all().count() == project.tasks.filter(status='completed').count()
    print("All tasks completed", all_tasks_completed)
    project.completed = all_tasks_completed
    project.save()