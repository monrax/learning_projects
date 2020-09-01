"""hyperjob URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from menu.views import MainPageView
from resume.views import IndexPageView as IndexResumes
from vacancy.views import IndexPageView as IndexVacancies
from vacancy.views import NewEntryView as VacancyEntry
from resume.views import SignUpView, LogInView, HomeView
from resume.views import NewEntryView as ResumeEntry

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainPageView.as_view()),
    path('resumes/', IndexResumes.as_view()),
    path('vacancies/', IndexVacancies.as_view()),
    path('login', LogInView.as_view()),
    path('signup', SignUpView.as_view()),
    path('home', HomeView.as_view()),
    path('resume/new', ResumeEntry.as_view()),
    path('vacancy/new', VacancyEntry.as_view()),
    path('login/', RedirectView.as_view(url='/login')),
    path('signup/', RedirectView.as_view(url='/signup')),
    path('home/', RedirectView.as_view(url='/home')),
    path('resume/new/', RedirectView.as_view(url='/resume/new')),
    path('vacancy/new/', RedirectView.as_view(url='/vacancy/new')),
]
