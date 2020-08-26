from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.views import View
from hypernews.settings import NEWS_JSON_PATH
from json import load, dumps
from datetime import datetime


def dict_by_link(list_dicts):
    try:
        by_link = {n['link']: n for n in list_dicts}
    except KeyError:
        return None
    return by_link


def load_news(json_path):
    # with open('..\\' + json_path) as news_json:
    with open(json_path) as news_json:
        news_list = load(news_json)
    return news_list


def append_news(json_path, entry):
    # with open('..\\' + json_path, 'rb+') as news_json:
    with open(json_path, 'rb+') as news_json:
        news_json.seek(-1, 2)
        news_json.write(b", " + entry.encode() + b']')


class MainPageView(View):
    def get(self, request, *args, **kwargs):
        return redirect("/news")


class IndexPageView(View):
    def get(self, request, *args, **kwargs):
        news = load_news(NEWS_JSON_PATH)
        if 'q' in request.GET:
            news = [n for n in news
                    if request.GET['q'].lower() in n['title'].lower()]
        news.sort(reverse=True,
                  key=(lambda d: datetime.strptime(d['created'],
                                                   "%Y-%m-%d %H:%M:%S")))
        return render(request, 'news/index.html', context={'news_list': news})


class NewsPageView(View):
    def get(self, request, *args, **kwargs):
        link = int(kwargs['link'])
        news_by_link = dict_by_link(load_news(NEWS_JSON_PATH))
        if link not in news_by_link:
            raise Http404
        return render(request, 'news/article.html',
                      context={'news': news_by_link[link]})


class CreatePageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'news/create.html', context={})

    def post(self, request, *args, **kwargs):
        new_link = max(dict_by_link(load_news(NEWS_JSON_PATH))) + 1
        new_entry = {'title': request.POST['title'],
                     'text': request.POST['text'],
                     'created': datetime.now().isoformat(sep=' ',
                                                         timespec='seconds'),
                     'link': new_link}
        append_news(NEWS_JSON_PATH, dumps(new_entry))
        return redirect("/news")
