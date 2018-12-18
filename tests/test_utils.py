# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from django.conf import settings
from django.test import TransactionTestCase
from django.urls import clear_url_caches, resolve, reverse

from cms.appresolver import clear_app_resolvers

from test_addon.models import Simple, Untranslated

from aldryn_translation_tools.utils import get_admin_url, get_object_from_request

from . import SimpleTransactionTestCase


class TestUtils(TransactionTestCase):

    def test_get_admin_url(self):
        # With pattern args, but no URL parameters
        change_action = 'auth_user_change'
        args = [1, ]
        kwargs = {}
        url = get_admin_url(change_action, args, **kwargs)
        self.assertIn('/admin/auth/user/1/', url)

        # With pattern args and a single URL parameter
        kwargs = {'alpha': 'beta', }
        url = get_admin_url(change_action, args, **kwargs)
        self.assertIn('/en/admin/auth/user/1/change/?alpha=beta', url)

        # With pattern args and two URL parameters
        kwargs = {'alpha': 'beta', 'gamma': 'delta', }
        url = get_admin_url(change_action, args, **kwargs)
        self.assertIn('/en/admin/auth/user/1/change/?alpha=beta&gamma=delta', url)

        # With pattern args and 3 URL parameters
        kwargs = {'a': 'b', 'g': 'd', 'e': 'z', }
        url = get_admin_url(change_action, args, **kwargs)
        self.assertIn('/en/admin/auth/user/1/change/?a=b&e=z&g=d', url)

        # With pattern args and numerical URL params
        kwargs = {'a': 1, 'g': 2, 'e': 3, }
        url = get_admin_url(change_action, args, **kwargs)
        self.assertIn('/en/admin/auth/user/1/change/?a=1&e=3&g=2', url)

        # With pattern args and odd-typed URL params
        kwargs = {'a': [], 'g': {}, 'e': None}
        url = get_admin_url(change_action, args, **kwargs)
        self.assertIn('/en/admin/auth/user/1/change/?a=%5B%5D&e=None&g=%7B%7D', url)

        # No pattern args...
        add_action = 'auth_user_add'
        kwargs = {'groups': 1, }
        url = get_admin_url(add_action, **kwargs)
        self.assertIn('/admin/auth/user/add/?groups=1', url)

        # No pattern args and no kwargs
        add_action = 'auth_user_add'
        url = get_admin_url(add_action)
        self.assertIn('/admin/auth/user/add/', url)


class TestToolbarHelpers(SimpleTransactionTestCase):

    def setUp(self):
        super(TestToolbarHelpers, self).setUp()
        self.reload_urls()

    def reload_urls(self):
        url_modules = [
            'cms.urls',
            'test_addon.urls',
            settings.ROOT_URLCONF,
        ]

        clear_app_resolvers()
        clear_url_caches()

        for module in url_modules:
            if module in sys.modules:
                del sys.modules[module]

    def test_get_obj_from_request(self):
        """ Test that we can get the object from the request. """
        self.simple1.set_current_language('en')
        slug_url = self.simple1.get_absolute_url('en')
        pk_url = slug_url.replace(
            '/{0}/'.format(self.simple1.slug),
            '/{0}/'.format(self.simple1.pk))

        for url in [slug_url, pk_url, ]:
            request = self.request_factory.get(url)
            request.LANGUAGE_CODE = 'en'
            request.current_page = self.page
            request.user = self.user
            request.resolver_match = resolve(request.path)

            simple = get_object_from_request(Simple, request)
            self.assertTrue(simple.pk, self.simple1.pk)

    def test_get_obj_from_empty_request(self):
        """ Test that we get None if the request doesn't contain an object. """
        request = self.request_factory.get(reverse('simple:simple-root'))
        request.LANGUAGE_CODE = 'en'
        request.current_page = self.page
        request.user = self.user
        request.resolver_match = resolve(request.path)
        simple = get_object_from_request(Simple, request)
        self.assertIsNone(simple)

    def test_get_untranslated_obj_from_request(self):
        """ Test that we can get a non-translated object from the request. """
        slug_url = self.untranslated1.get_absolute_url()
        pk_url = slug_url.replace(
            '/{0}/'.format(self.untranslated1.slug),
            '/{0}/'.format(self.untranslated1.pk))

        for url in [slug_url, pk_url, ]:
            request = self.request_factory.get(url)
            request.LANGUAGE_CODE = 'en'
            request.current_page = self.page
            request.user = self.user
            request.resolver_match = resolve(request.path)
            untranslated = get_object_from_request(Untranslated, request)
            self.assertTrue(untranslated.pk, self.untranslated1.pk)
