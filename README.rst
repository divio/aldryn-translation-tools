Aldryn Translation Tools
========================

A collection of shared helpers and mixins for translated django-CMS projects.

To use, install it into your project using pip::

    pip install aldryn-translation-tools


models.TranslationHelperMixin
-----------------------------

known_translation_getter()
~~~~~~~~~~~~~~~~~~~~~~~~~~

Signature::

    (value, language) = obj.known_translation_getter(field, default=None, language_code=None, any_language=False)

Acts like Parler's safe_translation_getter(), but respects the fallback
preferences as defined in `settings.CMS_LANGUAGES` and provides both the
translated value and the language it represents as a tuple.

This is especially helpful when resolving an object's absolute url for a given
language. If a fallback is used (respecting preference), then the returned
language_code can then be used to set the correct context for a reverse() to get
a URL consistent to the resulting language.

For example::

    from django.utils.translation import override

    from aldryn_translation_tools.models import TranslationHelperMixin
    from cms.utils.i18n import get_current_language
    from parler.models import TranslatableModel, TranslatedFields

    class Fruit(TranslationHelperMixin, TranslatableModel):
        translations = TranslatableFields(
            name=models.CharField(...),
            slug=models.CharField(...)
        )

        def get_absolute_url(self, language=None):
            language = language or get_current_language()
            (slug, language) = self.known_translation_getter('slug',
                default=None, language_code=language, any_language=False)
            with override(language):
                return reverse('fruit-detail', kwargs={'slug': slug})

In contrast, if we had only done something like this::

    ...

        def get_absolute_url(self, language=None)
            language = language or get_current_language()
            slug = self.safe_translation_getter('slug', default=None,
                language_code=language, any_language=False)
            with override(language):
                return reverse('fruit-detail', kwargs={'slug': slug})

If the fruit `apple` has not yet been translated to FR it is possible that
you'll end up with the slug in a fallback langauge, and the rest of the URL in
the desired language, so instead of getting a language-consistent fallback url::

    /en/apple/

You might get::

    /fr/apple/

Which, at best, would be confusing for site visitors but more likely won't exist
resulting in a NoReverseFound exception and which clearly is not respecting the
fallback preferences set by the developer.
