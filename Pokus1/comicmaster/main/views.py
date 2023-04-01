from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class HomeView(LoginRequiredMixin, View):
    login_url = '/account'
    
    def get(self, request):
        return render(request, "main/home.html", {})