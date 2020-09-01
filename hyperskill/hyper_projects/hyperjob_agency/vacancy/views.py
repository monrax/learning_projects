from django.views import View
from django.views.defaults import HttpResponseForbidden
from django.shortcuts import render, redirect
from .models import Vacancy


class IndexPageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'listing.html',
                      context={'items': Vacancy.objects.all()})

class NewEntryView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return render(request, 'create.html',
                          context={'type': "vacancy"})
        else:
            return HttpResponseForbidden("<h1>You're not a manager!</h1>")

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            Vacancy.objects.create(author=request.user,
                                   description=request.POST['description'])
            return redirect('/')
        else:
            return HttpResponseForbidden("<h1>You're a manager!</h1>")
