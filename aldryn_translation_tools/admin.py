# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings

from cms.utils.i18n import get_current_language
from cms.utils.urlutils import admin_reverse


class AllTranslationsMixin(object):
    class Media:
        css = {'all': ('css/admin/all-translations-mixin.css', ), }

    def all_translations(self, obj):
        """
        Adds a property to the list_display that lists all translations with
        links directly to their change forms. Includes CSS to style the links to
        looks like tags with color indicating current language, active and
        inactive translations.

        A similar capability is in HVAD, and now there is this for
        Parler-based projects.
        """
        available = list(obj.get_available_languages())
        current = get_current_language()
        langs = []
        for code, lang_name in settings.LANGUAGES:
            classes = ["lang-code", ]
            title = lang_name
            if code == current:
                classes += ["current", ]
            if code in available:
                classes += ["active", ]
                title += " (translated)"
            else:
                title += " (untranslated)"
            change_form_url = admin_reverse(
                '{app_label}_{model_name}_change'.format(
                    app_label=obj._meta.app_label.lower(),
                    model_name=obj.__class__.__name__.lower(),
                ), args=(obj.id, )
            )
            link = ('<a class="{classes}" href="{url}?language={code}" ' +
                'title="{title}">{code}</a>').format(
                classes=' '.join(classes),
                url=change_form_url,
                code=code,
                title=title,
            )
            langs.append(link)
        return ''.join(langs)
    all_translations.short_description = 'Translations'
    all_translations.allow_tags = True

    def get_list_display(self, request):
        """
        Unless the the developer has already placed "all_translations" in the
        list_display list (presumably specifically where she wants it), append
        the list of translations to the end.
        """
        list_display = super(
            AllTranslationsMixin, self).get_list_display(request)
        if 'all_translations' not in list_display:
            list_display = list(list_display) + ['all_translations', ]
        return list_display
