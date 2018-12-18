# -*- coding: utf-8 -*

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class SimpleApp(CMSApp):
    name = _('Simple')
    app_name = 'simple'

    def get_urls(self, page=None, language=None, **kwargs):
        return ["test_addon.urls"]


apphook_pool.register(SimpleApp)
