# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from cms.utils.i18n import get_current_language, get_fallback_languages


class TranslationHelperMixin(object):
    def known_translation_getter(self, field, default=None,
                                 language_code=None, any_language=False):
        """
        This is meant to act like HVAD/Parler's safe_translation_getter() but
        respects the fallback preferences as defined in `settings.CMS_LANGUAGES`
        and returns both the translated field value and the language it
        represents as a tuple: (value, language).

        If no suitable language is found, then it returns (default, None)
        """
        # NOTE: We're using the CMS fallbacks here, rather than the Parler
        # fallbacks, the developer should ensure that their project's Parler
        # settings match the CMS settings.
        try:
            object_languages = self.get_available_languages()
            assert hasattr(object_languages, '__iter__')
        except [KeyError, AssertionError]:
            raise ImproperlyConfigured("TranslationHelperMixin must be used "
                "with a model defining get_available_languages() that returns "
                "a list of available language codes. E.g., django-parler's "
                "TranslatableModel.")
        language_code = language_code or get_current_language()
        if language_code not in object_languages:
            # OK, we're going to have to use a fallback language
            fallbacks = get_fallback_languages(language_code)
            # Grab the first language from fallbacks that is also a known
            # translation of the article.
            language_code = next(
                (lang for lang in fallbacks if lang in object_languages), None)
            if not language_code:
                # No fallbacks were available either
                if any_language:
                    # We're allowed to use any old language, grab the first one
                    language_code = next(object_languages, None)
                    if not language_code:
                        # The object appears to have no translations at all.
                        return (default, None)
                else:
                    return (default, None)

        value = self.safe_translation_getter(
            field, default=default, language_code=language_code)
        return (value, language_code)
