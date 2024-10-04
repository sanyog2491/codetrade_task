from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import ProjectForm, TaskForm
from .models import Project, Task
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.db.models import Q


class CustomLoginView(auth_views.LoginView):
    template_name = 'registration/login.html' 

    def get_success_url(self):
        return reverse_lazy('project_list') 
    
class CustomLogoutView(auth_views.LoginView):

    def get_success_url(self):
        return reverse_lazy('login') 
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def create_project(request):
    users = User.objects.all()  
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m() 

            messages.success(request, f"Project '{project.name}' created successfully!")
            return redirect('project_list')
    else:
        form = ProjectForm()

    return render(request, 'project_task/project_form.html', {'form': form, 'users': users})

# def project_list(request):
#     projects = Project.objects.all()  
#     return render(request, 'project_task/project_list.html', {'projects': projects})

def project_list(request):
    user = request.user

    projects = Project.objects.filter(Q(created_by=user) | Q(assigned_users=user))

    return render(request, 'project_task/project_list.html', {'projects': projects})


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id) 
    return render(request, 'project_task/project_detail.html', {'project': project})

# @login_required
# def edit_project(request, project_id):
#     project = get_object_or_404(Project, id=project_id)

#     if request.user != project.created_by and request.user not in project.assigned_users.all():
#         messages.warning(request, "You don't have permission to modify this project.")
#         return redirect('project_list') 

#     if request.method == 'POST':
#         form = ProjectForm(request.POST, instance=project)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Project updated successfully.")
#             return redirect('project_list')
#     else:
#         form = ProjectForm(instance=project)

#     return render(request, 'project_task/edit_project.html', {'form': form, 'project': project})

def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            
            if hasattr(project, '_messages_list'):
                for msg in project._messages_list:
                    messages.info(request, msg)  

            messages.success(request, "Project updated successfully!")
            return redirect('project_list')

    else:
        form = ProjectForm(instance=project)

    return render(request, 'project_task/edit_project.html', {'form': form, 'project': project})

def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.user != project.created_by and request.user not in project.assigned_users.all():
        messages.warning(request, "You don't have permission to modify this project.")
        return redirect('project_list') 
    
    if request.method == 'POST':
        project.delete() 
        messages.success(request, 'Project deleted successfully.')
        return redirect('project_list') 
    return render(request, 'project_task/delete_project.html', {'project': project}) 

def create_task(request):
    project = Project.objects.all()  
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            form.save_m2m() 
            
            messages.success(request, f"Task '{task.name}' created successfully!")
            return redirect('task_list')
        else:
            print(form.errors) 
    else:
        form = TaskForm()
        
    return render(request, 'project_task/task_templates/task_form.html', {'form': form, 'projects': project})

def task_list(request):
    tasks = Task.objects.all()  
    return render(request, 'project_task/task_templates/task_list.html', {'tasks': tasks})

def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id) 
    return render(request, 'project_task/task_templates/task_view.html', {'task': task})

def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id) 
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('task_list') 
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'project_task/task_templates/task_update.html', {'form': form, 'task': task})

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete() 
        messages.success(request, 'Task deleted successfully.')
        return redirect('task_list') 
    return render(request, 'project_task/task_templates/task_delete.html', {'task': task}) 
