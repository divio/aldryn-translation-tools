# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from slugify import slugify

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
try:
    from django.utils.encoding import force_text
except ImportError:  # pragma: no cover
    from django.utils.encoding import force_unicode as force_text
from django.utils.translation import ugettext_lazy as _

from cms.utils.i18n import (
    get_current_language,
    get_default_language,
    get_fallback_languages,
)


class TranslatedAutoSlugifyMixin(object):
    """
    This is a TranslatableModel mixin that automatically generates a suitable
    slug for the object on save.

    If `slug_globally_unique` is True, then slugs will be required to be
    unique across all languages.

    If `slug_globally_unique` is False (default), then the strategy used here
    is that it is OK for two objects to use the same slug if the slugs are for
    different languages. So if this were used on an Article model, these would
    be valid:

        /en/pain -> Article in EN about physical discomfort
        /fr/pain -> Article in FR about bread

    Of course, this means that when resolving an object from its URL, care must
    be taken to factor in the language segment of the URL too.
    """

    # Default slug to use if the current object produces an empty slug. A
    # default is assembled via introspection. Implementing class should provide
    # a lazy translated string here.
    slug_default = None
    # The translated slug field name.
    slug_field_name = 'slug'
    # Flag controlling if slugs are unique per language or globally unique.
    slug_globally_unique = False
    # Max length of the slug. By default is determined by introspection.
    slug_max_length = None
    # The separator to use before any index.
    slug_separator = '-'
    # The translated field to derive a slug from. If `get_slug_source()` is
    # overridden in the model, overriding `get_slug_default` is recommended.
    slug_source_field_name = None
    # filters that would be used to determine slug uniqueness, would be
    # populated with slug_field_name.
    raw_slug_filter_string = 'translations__{0}'

    # python-slugify option for smart truncate
    word_boundary = False
    # python-slugify option for smart truncate
    save_order = True

    def get_slug_default(self):
        """
        Naively constructs a translated default slug from the object. For
        better results, just set the `slug_default` property on the class to a
        lazy translated string. Alternatively, override this method if you need
        to more programmatically determine the default slug.

        Example: If your model is "news article" and your source field is
        "title" this will return "news-article-without-title".
        """
        if self.slug_default:
            # Implementing class provides its own, translated string, use it.
            return force_text(self.slug_default)

        object_name = self._meta.verbose_name

        # Introspect the field name
        try:
            trans_meta = self.translations.model._meta
            source_field = trans_meta.get_field(
                self.slug_source_field_name)
            field_name = getattr(source_field, 'verbose_name')
        except:
            field_name = _('name')

        slug_default = _("{0}-without-{1}").format(
            slugify(force_text(object_name)),
            slugify(force_text(field_name)),
        )
        return slug_default

    def get_slug_max_length(self, idx_len=0):
        """
        Introspects the slug field to determine the max length, taking into
        account a possible separator and up to a [idx_len]-digit number.
        """
        if self.slug_max_length:
            slug_max_length = self.slug_max_length
        else:
            trans_meta = self.translations.model._meta
            slug_field = trans_meta.get_field(self.slug_field_name)
            max_length = getattr(slug_field, 'max_length', 255)
            # All objects of this class will use the same value.
            slug_max_length = max_length
        if idx_len:
            return slug_max_length - len(self.slug_separator) - idx_len
        return slug_max_length

    def get_slug_source(self):
        """
        Simply returns the value of the slug source field. Override for more
        complex situations such as using multiple fields as the source.
        """
        return getattr(self, self.slug_source_field_name, None)

    def _get_candidate_slug(self, slug, idx=0):
        return "{slug}{sep}{idx}".format(
            slug=slug, sep=self.slug_separator, idx=idx)

    def _get_existing_slug(self):
        """
        Get slug if it is set on object, slug is taken from
        `self.slug_field_name` field.
        """
        return getattr(self, self.slug_field_name, None)

    def slugify(self, text, max_length=None):
        """
        Generate slug using appropriate slugification utility.
        """
        if max_length is None:
            max_length = self.get_slug_max_length()
        slug = slugify(text,
                       max_length=max_length,
                       word_boundary=self.word_boundary,
                       save_order=self.save_order,
                       separator=self.slug_separator)
        return slug

    def _get_ideal_slug(self):
        """Build the "ideal slug" for this object as a starting point"""
        source = self.get_slug_source()
        if source:
            source = force_text(source)
            ideal_slug = force_text(self.slugify(source))
        else:
            # For some reason, the slug came back empty, use the default
            ideal_slug = force_text(self.get_slug_default())

        # Trim the length of the ideal slug to the limit allowed the field
        max_length = self.get_slug_max_length()
        return ideal_slug[:max_length]

    def _get_slug_queryset(self, lookup_model=None):
        """
        Build the queryset we will be using considering options and the
        object's state.
        lookup model - model manager to build base queryset. If none
        self.__class__ would be used.
        """
        language = self.get_current_language() or get_default_language()
        if lookup_model is None:
            lookup_model = self.__class__

        qs = lookup_model.objects.language(language)
        if not self.slug_globally_unique:
            qs = qs.filter(
                translations__language_code=language)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        return qs

    def _slug_exists(self, slug, slug_filter=None, qs=None):
        """
        Check if slug exists in the given queryset.
        If slug_filter is None it would be created from
        self.raw_slug_filter_string and self.slug_field_name
        """

        if qs is None:
            qs = self._get_slug_queryset()
        if slug_filter is None:
            slug_filter = self.raw_slug_filter_string.format(
                self.slug_field_name)
        return qs.filter(**{slug_filter: slug}).exists()

    def make_new_slug(self, slug=None, qs=None):
        """
        Generate a slug that meets requirements.
        :param qs: queryset to check uniqueness,
                   if None - self._get_slug_queryset() queryset will be used
        :param slug: candidate slug, new slug would be generated from this
                     value, if None - self._get_ideal_slug() would be used
        :return (str): slug
        """

        if not slug:
            # Build the "ideal slug" for this object as a starting point
            slug = self._get_ideal_slug()
        # initial setup
        idx = 1
        candidate = slug
        max_length = self.get_slug_max_length()
        # Check if the resulting slug is currently in use, if not, use it.
        # Otherwise, add a separator and an index until we find an
        # unused combination.
        while self._slug_exists(candidate, qs=qs):
            if len(candidate) > max_length:
                max_length = self.get_slug_max_length(len(str(idx)))
            candidate = self._get_candidate_slug(slug[:max_length], idx)
            idx += 1
        return candidate

    def save(self, **kwargs):
        slug = self._get_existing_slug()
        if not slug or self._slug_exists(slug):
            slug = self.make_new_slug(slug=slug)
            setattr(self, self.slug_field_name, slug)
        return super(TranslatedAutoSlugifyMixin, self).save(**kwargs)


class TranslationHelperMixin(object):

    def known_translation_getter(self, field, default=None,
                                 language_code=None, any_language=False):
        """
        This is meant to act like HVAD/Parler's safe_translation_getter() but
        respects the fallback preferences as defined in
        `settings.CMS_LANGUAGES` and returns both the translated field value
        and the language it represents as a tuple: (value, language).

        If no suitable language is found, then it returns (default, None)
        """
        # NOTE: We're using the CMS fallbacks here, rather than the Parler
        # fallbacks, the developer should ensure that their project's Parler
        # settings match the CMS settings.
        try:
            object_languages = self.get_available_languages()
            assert hasattr(object_languages, '__iter__')
        except [KeyError, AssertionError]:
            raise ImproperlyConfigured(
                "TranslationHelperMixin must be used with a model defining"
                "get_available_languages() that returns a list of available"
                "language codes. E.g., django-parler's TranslatableModel.")

        language_code = (
            language_code or get_current_language() or get_default_language())
        site_id = getattr(settings, 'SITE_ID', None)
        languages = [language_code] + get_fallback_languages(
            language_code, site_id=site_id)

        # Grab the first language that is common to our list of fallbacks and
        # the list of available languages for this object.
        if languages and object_languages:
            language_code = next(
                (lang for lang in languages if lang in object_languages), None)

            if language_code:
                value = self.safe_translation_getter(field,
                    default=default, language_code=language_code)
                return (value, language_code)

        # No suitable translation exists
        return (default, None)
