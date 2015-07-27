# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from aldryn_translation_tools.models import TranslatedAutoSlugifyMixin
from parler.models import TranslatableModel, TranslatedFields


@python_2_unicode_compatible
class Simple(TranslatedAutoSlugifyMixin, TranslatableModel):
    slug_source_field_name = 'name'

    translations = TranslatedFields(
        name=models.CharField(max_length=64),
        slug=models.SlugField(max_length=64, blank=True, default='')
    )

    def __str__(self):
        return self.safe_translation_getter(
            'name', default="Simple: {0}".format(self.pk))


@python_2_unicode_compatible
class Unconventional(TranslatedAutoSlugifyMixin, TranslatableModel):
    slug_source_field_name = 'title'
    slug_field_name = 'unique_slug'

    translations = TranslatedFields(
        title=models.CharField(_('short title'), max_length=64),
        unique_slug=models.SlugField(max_length=64, blank=True, default='')
    )

    class Meta:
        verbose_name = _('unconventional model')

    def __str__(self):
        return self.safe_translation_getter(
            'title', default="Unconventional: {0}".format(self.pk))


class Complex(TranslatedAutoSlugifyMixin, TranslatableModel):

    translations = TranslatedFields(
        name=models.CharField(max_length=64),
        slug=models.SlugField(max_length=64, blank=True, default='')
    )

    object_type = models.CharField(max_length=64)

    def get_slug_source(self):
        if self.object_type and self.name:
            return "{type}: {name}".format(
                type=self.object_type,
                name=self.safe_translation_getter('name', default='unnamed')
            )
        else:
            return None

    def __str__(self):
        return self.get_slug_source()
