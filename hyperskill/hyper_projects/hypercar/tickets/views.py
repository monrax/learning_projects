from django.views import View
from django.http.response import HttpResponse, Http404
from django.shortcuts import render, redirect

ticket_id = 0
next_ticket = 0
line_of_cars = {"change_oil": [], "inflate_tires": [], "diagnostic": []}


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


class MenuView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/menu.html')


class TicketView(View):
    def get(self, request, *args, **kwargs):
        global ticket_id
        estimated_time = 0
        req_service = kwargs["service_type"]
        if req_service in line_of_cars:
            for i, service in enumerate(line_of_cars):
                estimated_time += len(line_of_cars[service]) * (lambda x: 11*x**2 - 8*x + 2)(i)
                if req_service == service:
                    break
            ticket_id += 1
            line_of_cars[req_service].append(ticket_id)
            return render(request, "tickets/ticket.html",
                          context={"ticket_number": ticket_id,
                                   "minutes_to_wait": estimated_time})
        else:
            raise Http404


class ProcessView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request, "tickets/processing.html",
            context={"queue": [len(i) for i in line_of_cars.values()]}
        )

    def post(self, request, *args, **kwargs):
        global next_ticket
        if any(line_of_cars.values()):
            for service in line_of_cars:
                if line_of_cars[service]:
                    next_ticket = line_of_cars[service].pop(0)
                    break
        else:
            next_ticket = 0
        return redirect("/next")


class NextClientView(View):
    def get(self, request, *args, **kwargs):
        global next_ticket
        return render(request, "tickets/next.html",
                      context={"number_of_ticket": next_ticket})
