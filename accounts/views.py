from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm, UserRegistrationForm
import logging

logger = logging.getLogger(__name__)

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome back, {username}!')
                return redirect('profiles:profile')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home:index')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        print(f"Form is valid: {form.is_valid()}")
        print(f"Form errors: {form.errors}")
        
        if not form.is_valid():
            return render(request, 'accounts/register.html', {'form': form})
        
        try:
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('profiles:profile')
        except Exception as e:
            print(f"Error during save: {e}")
            return render(request, 'accounts/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})