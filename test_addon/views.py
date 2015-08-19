# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import DetailView, ListView, TemplateView

from parler.views import TranslatableSlugMixin

from .models import Simple, Untranslated


class SimpleRootView(TemplateView):
    template = 'test_addon/empty.html'


class SimpleListView(ListView):
    model = Simple
    http_method_names = ['get', ]


class SimpleDetailView(TranslatableSlugMixin, DetailView):
    model = Simple
    view_url_name = 'thing-detail'


class UntranslatedDetailView(DetailView):
    model = Untranslated
    view_url_name = 'untranslated-detail'
