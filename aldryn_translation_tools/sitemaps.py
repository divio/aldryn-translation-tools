# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import NoReverseMatch
from django.contrib.sitemaps import Sitemap
from django.utils import translation


class I18NSitemap(Sitemap):
    """
    A helper class that supports translated sitemaps.

    In sitemaps.py (example):

        class ThingsSitemap(I18NSitemap):
            changefreq = "weekly"
            priority = 0.75

            def items(self):
                # Make sure to limit items to those translated into the language
                # set in self.language.
                return Thing.objects.published().translated(self.language).all()

    Then, in urls.py, when setting up the sitemaps dictionary, use as normal,
    but instantiate the class with a language.

        sitemaps = {
            # Specify non-translated apps as usual
            'janky_app': JankyAppSitemap,

            # Translated Apps
            'things-en': ThingsSitemap('en'),
            'things-fr': ThingsSitemap('fr'),
            'things-de': ThingsSitemap('de'),
            ...
        }

    Continue as normal.
    """

    def __init__(self, language=None):
        """
        Override's Sitemap's constructor to accept a language code as
        a parameter.
        """
        super(I18NSitemap, self).__init__()
        self.language = language or settings.LANGUAGES[0][0]

    def location(self, item):
        """
        Overrides Sitemap.location() to utilise the language set in
        self.language.
        """
        with translation.override(self.language):
            try:
                return item.get_absolute_url()
            except NoReverseMatch:  # pragma: no cover
                # Note, if we did our job right in items(), this
                # shouldn't happen at all, but just in case...
                return ''
