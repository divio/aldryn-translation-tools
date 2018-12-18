# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import random
import string

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sites.models import Site
from django.test import RequestFactory, TransactionTestCase
from django.utils.translation import override

from cms import api
from cms.models import Title
from cms.utils.conf import get_cms_setting
from cms.utils.i18n import get_language_list

from djangocms_helper.utils import create_user
from parler.utils.context import switch_language
from test_addon.models import Simple, Untranslated


class TestUtilityMixin(object):
    @staticmethod
    def reload(obj, language=None):
        """
        Simple convenience method for re-fetching an object from the ORM,
        optionally "as" a specified language.
        """
        try:
            new_obj = obj.__class__.objects.language(language).get(id=obj.id)
        except Exception:
            new_obj = obj.__class__.objects.get(id=obj.id)
        return new_obj

    """Just adds some common test utilities to the testing class."""
    @staticmethod
    def rand_str(prefix='', length=16, chars=string.ascii_letters):
        return prefix + ''.join(random.choice(chars) for _ in range(length))

    def assertEqualItems(self, a, b):
        try:
            # In Python3, this method has been renamed (poorly)
            return self.assertCountEqual(a, b)
        except Exception:
            # In 2.6, assertItemsEqual() doesn't sort first
            return self.assertItemsEqual(sorted(a), sorted(b))


class SimpleTestMixin(TestUtilityMixin):
    """This mixin adds data and methods useful for testing Things."""
    data = {
        'simple1': {
            'de': {'name': 'Objekt eins', },
            'en': {'name': 'Simple one', },
            'fr': {'name': 'objet un'},
        },
        'simple2': {
            'de': {'name': 'Objekt zwei', },
            'en': {'name': 'Simple two', },
            'fr': {'name': 'objet deux', },
        },
        'untranslated1': {
            'name': 'Untranslated Object',
            'slug': 'untranslated-object',
        }
    }

    simple1 = None
    simple2 = None
    untranslated1 = None

    def setUp(self):
        super(SimpleTestMixin, self).setUp()
        with override('de'):
            self.simple1 = Simple()
            self.simple1.name = self.data['simple1']['de']['name']
            self.simple1.save()

            self.simple2 = Simple()
            self.simple2.name = self.data['simple2']['de']['name']
            self.simple2.save()

        for lc in ['en', 'fr']:
            with switch_language(self.simple1, lc):
                self.simple1.name = self.data['simple1'][lc]['name']
                self.simple1.save()
            with switch_language(self.simple2, lc):
                self.simple2.name = self.data['simple2'][lc]['name']
                self.simple2.save()

        if not self.untranslated1:
            self.untranslated1 = Untranslated(**self.data['untranslated1'])
            self.untranslated1.save()


class CMSRequestBasedTest(TestUtilityMixin, TransactionTestCase):
    """Sets-up User(s) and CMS Pages for testing."""
    languages = get_language_list()

    @classmethod
    def setUpClass(cls):
        cls.request_factory = RequestFactory()
        if not User.objects.filter(username='normal').count():
            cls.user = create_user('normal', 'normal@admin.com', 'normal')
        cls.site1 = Site.objects.get(pk=1)

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()

    def setUp(self):
        super(CMSRequestBasedTest, self).setUp()
        self.template = get_cms_setting('TEMPLATES')[0][0]
        self.language = settings.LANGUAGES[0][0]
        self.root_page = api.create_page(
            'root page',
            self.template,
            self.language,
            published=True,
        )

        self.page = api.create_page(
            'Simple Page',
            self.template,
            self.language,
            published=True,
            parent=self.root_page,
            apphook='SimpleApp',
            apphook_namespace='simple',
        )

        self.placeholder = self.page.placeholders.all()[0]
        self.request = self.get_request('en')

        for page in [self.root_page, self.page]:
            for language, _ in settings.LANGUAGES[1:]:
                api.create_title(language, page.get_slug(), page)
                page.publish(language)

    @classmethod
    def get_request(cls, language=None, url="/"):
        """
        Returns a Request instance populated with cms specific attributes.
        """
        request = cls.request_factory.get(url)
        request.session = {}
        request.LANGUAGE_CODE = language or settings.LANGUAGE_CODE
        # Needed for plugin rendering.
        request.current_page = None
        request.user = AnonymousUser()
        return request

    def get_or_create_page(self, base_title=None, languages=None):
        """Creates a page with a given title, or, if it already exists, just
        retrieves and returns it."""
        from cms.api import create_page, create_title
        if not base_title:
            # No title? Create one.
            base_title = self.rand_str(prefix="page", length=8)
        if not languages:
            # If no langs supplied, use'em all
            languages = self.languages
        # If there is already a page with this title, just return it.
        try:
            page_title = Title.objects.get(title=base_title)
            return page_title.page.get_draft_object()
        except Exception:
            pass

        # No? Okay, create one.
        page = create_page(base_title, 'fullwidth.html', language=languages[0])
        # If there are multiple languages, create the translations
        if len(languages) > 1:
            for lang in languages[1:]:
                title_lang = "{0}-{1}".format(base_title, lang)
                create_title(language=lang, title=title_lang, page=page)
                page.publish(lang)
        return page.get_draft_object()

    def get_page_request(
            self, page, user, path=None, edit=False, lang_code='en'):
        from cms.middleware.toolbar import ToolbarMiddleware
        path = path or page and page.get_absolute_url()
        if edit:
            path += '?edit'
        request = RequestFactory().get(path)
        request.session = {}
        request.user = user
        request.LANGUAGE_CODE = lang_code
        if edit:
            request.GET = {'edit': None}
        else:
            request.GET = {'edit_off': None}
        request.current_page = page
        mid = ToolbarMiddleware()
        mid.process_request(request)
        return request


class SimpleTransactionTestCase(SimpleTestMixin, CMSRequestBasedTest):
    pass
