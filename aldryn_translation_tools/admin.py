# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.forms import widgets
from django.utils.translation import force_text, ugettext as _

from cms.utils.i18n import get_current_language
from cms.utils.urlutils import admin_reverse


class LinkedRelatedInlineMixin(object):
    """
    This InlineAdmin mixin links the first field to the row object's own admin
    change form.

    NOTE: If the first field is editable, it is undefined what will happen.
    For best results, consider making all fields readonly (since they can be
    edited with ease by following the link), and disabling the ability to add
    new objects by overriding has_add_permission() on the inline to always
    return false.
    """

    extra = 0

    class ReverseLink:

        allow_tags = True

        def __init__(self, display_link="link"):
            self.display_link = display_link
            self.short_description = display_link

        def __call__(self, obj):
            model_name = obj.__class__.__name__.lower()
            admin_link = admin_reverse(
                "{app_label}_{model_name}_change".format(
                    app_label=obj._meta.app_label.lower(),
                    model_name=model_name,
                ), args=(obj.id, ))
            return '<a href="{admin_link}" title="{title}">{link}</a>'.format(
                admin_link=admin_link,
                title=_('Click to view or edit this {0}').format(
                    obj._meta.verbose_name),
                link=getattr(obj, self.display_link))

    def __init__(self, parent_model, admin_site):
        self.original_fields = self.get_fields_list(None)
        if len(self.original_fields):
            self.fields = ["reverse_link", ] + self.original_fields[1:]
        else:
            self.fields = ["reverse_link"]
        self.reverse_link = self.ReverseLink(self.original_fields[0])
        super(LinkedRelatedInlineMixin, self).__init__(
            parent_model, admin_site)

    def get_fields_list(self, request, obj=None):
        """
        Returns a list of the AdminModel's declared `fields`, or, constructs it
        from the object, then, removes any `exclude`d items.
        """
        # ModelAdmin.get_fields came in Django 1.7, I believe
        if hasattr(super(LinkedRelatedInlineMixin, self), "get_fields"):
            fields = super(
                LinkedRelatedInlineMixin, self).get_fields(request, obj)
        elif self.fields:
            fields = self.fields
        else:
            fields = [f.name for f in self.model._meta.local_fields]
        if fields and self.exclude:
            fields = [f for f in fields if f not in self.exclude]
        if fields:
            return list(fields)
        else:
            return []

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(
            LinkedRelatedInlineMixin, self).get_readonly_fields(request, obj)
        if "reverse_link" not in readonly_fields:
            readonly_fields = list(readonly_fields) + ["reverse_link", ]
        # We want all fields to be readonly for this inline
        return readonly_fields


class AllTranslationsMixin(object):

    @property
    def media(self):
        return super(AllTranslationsMixin, self).media + widgets.Media(
            css={'all': ('css/admin/all-translations-mixin.css', ), }
        )

    def all_translations(self, obj):
        """
        Adds a property to the list_display that lists all translations with
        links directly to their change forms. Includes CSS to style the links
        to looks like tags with color indicating current language, active and
        inactive translations.

        A similar capability is in HVAD, and now there is this for
        Parler-based projects.
        """
        available = list(obj.get_available_languages())
        current = get_current_language()
        langs = []
        for code, lang_name in settings.LANGUAGES:
            classes = ["lang-code", ]
            title = force_text(lang_name)
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
