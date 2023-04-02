from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, 'account/login.html')
        
    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is None:
            messages.error(request, 'Invalid password or username')
            return render(request, 'account/login.html')
        else:
            login(request, user)
            return redirect('/')
 

class RegisterView(View):
    def get(self, request):
        return render(request, 'account/register.html')

    def post(self, request):
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 != password2:
            messages.success(request, "Passwords not matching")
            return render(request, 'account/register.html')
        
        user = User.objects.create_user(username=email, email=email, password=password1)
        login(request, user)
        return redirect('/')


class LogoutView(LoginRequiredMixin, View):
    login_url = '/account'

    def get(self, request):
        logout(request)
        return redirect('/account')