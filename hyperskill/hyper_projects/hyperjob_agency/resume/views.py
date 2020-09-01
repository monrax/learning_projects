from django.views import View
from django.shortcuts import render, redirect
from django.views.defaults import HttpResponseForbidden
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from .models import Resume


class IndexPageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'listing.html',
                      context={'items': Resume.objects.all()})


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = 'login'
    template_name = 'signup.html'


class LogInView(LoginView):
    redirect_authenticated_user = True
    template_name = 'login.html'


class HomeView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect("/vacancy/new")
            else:
                return redirect("/resume/new")
        else:
        #     return HttpResponseForbidden("<h1>You're not logged in!</h1>")
            return redirect("/")


class NewEntryView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return render(request, 'create.html',
                          context={'type': "resume"})
        else:
            return HttpResponseForbidden("<h1>You're a manager!</h1>")

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            Resume.objects.create(author=request.user,
                                  description=request.POST['description'])
            return redirect('/')
        else:
            return HttpResponseForbidden("<h1>You're not a manager!</h1>")
