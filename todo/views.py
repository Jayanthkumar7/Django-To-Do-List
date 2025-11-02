from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Task


# 🔹 Register a new user
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Something went wrong. Please try again.')
    else:
        form = UserCreationForm()
    return render(request, 'todo/register.html', {'form': form})


# 🔹 Login view
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('tasks')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'todo/login.html')


# 🔹 Logout view
def logout_user(request):
    logout(request)
    return redirect('login')


# 🔹 List all tasks (only for logged-in users)
@login_required(login_url='/login/')
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    # Search
    search_query = request.GET.get('q') or ''
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    # Filter
    filter_option = request.GET.get('filter', 'all')
    if filter_option == 'completed':
        tasks = tasks.filter(complete=True)
    elif filter_option == 'pending':
        tasks = tasks.filter(complete=False)

    return render(request, 'todo/task_list.html', {
        'tasks': tasks,
        'search_query': search_query,
    })


# 🔹 Create a new task (only for logged-in users)
@login_required(login_url='/login/')
def task_create(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST.get('description', '')
        Task.objects.create(user=request.user, title=title, description=description)
        messages.success(request, 'Task created successfully!')
        return redirect('tasks')
    return render(request, 'todo/task_form.html')


# 🔹 Update a task (only for logged-in users)
@login_required(login_url='/login/')
def task_update(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    if request.method == 'POST':
        task.title = request.POST['title']
        task.description = request.POST.get('description', '')
        task.complete = 'complete' in request.POST
        task.save()
        messages.success(request, 'Task updated successfully!')
        return redirect('tasks')
    return render(request, 'todo/task_form.html', {'task': task})


# 🔹 Delete a task (only for logged-in users)
@login_required(login_url='/login/')
def task_delete(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted.')
        return redirect('tasks')
    return render(request, 'todo/task_delete.html', {'task': task})
