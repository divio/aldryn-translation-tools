Aldryn Translation Tools
========================

A collection of shared helpers and mixins for translated django-CMS projects.

To use, install it into your project using pip::

    pip install aldryn-translation-tools


admin.AllTranslationsMixin
--------------------------

Automatically adds a list of language "tags" in the changelist. Tag color
indicates the state of translation for that object. Grey meaning untranslated,
blue meaning translated. Darker versions of each are used to indicate the
current language.

Each tag is linked to the specific language tag on the change form of the
object.

A similar capability is in HVAD, and now there is this for Parler-based
projects.

Preview:

.. image:: https://cloud.githubusercontent.com/assets/615759/7727430/5889f0e0-ff11-11e4-930a-2bfc80bef426.jpg

To use this, merely import and add the mixin to your Model Admin class: ::

    from parler.admin import TranslatableAdmin
    from aldryn_translation_tools.admin import AllTranslationsMixin

    class GroupAdmin(AllTranslationsMixin, TranslatableAdmin):
       # ....

If you wish to put the tags into a different column, you can add
`all_translations` to the list_display list wherever you'd like, otherwise the
"Languages" column will automatically be placed on the far right.


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

Then, if the fruit `apple` has not yet been translated to FR it is possible that
you'll end up with the slug in a fallback langauge, and the rest of the URL in
the requested language, so instead of getting a language-consistent fallback
url::

    /en/apple/

You might get::

    /fr/apple/

Which, at best, would be confusing for site visitors but more likely won't exist
resulting in a NoReverseFound exception or 404 and which clearly is not
respecting the fallback preferences set by the developer.
