Aldryn Translation Tools
========================

|PyPI Version| |Coverage status|

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


admin.LinkedRelatedInlineMixin
------------------------------

This admin inline mixin links the first field to the row object's own admin
change form.

If the first field is editable, results are undefined but probably won't work
as expected. For best results, consider making all fields readonly (since they
can be edited with ease by following the link), and disabling the ability to
add new objects by overriding has_add_permission() on the inline to always
return ``False``.


models.TranslatedAutoSlugMixin
------------------------------

This is a TranslatableModel mixin that automatically generates a suitable
slug for the object on ``save()``.

If ``slug_globally_unique`` is ``True``, then slugs will be required to be
unique across all languages.

If ``slug_globally_unique`` is ``False`` (default), then the strategy used here
is that it is OK for two objects to use the same slug if the slugs are for
different languages. So if this were used on a translated Article model, these
URLs would be valid:

``/en/pain`` - An article in EN about physical discomfort

``/fr/pain`` - An article in FR about bread

Of course, this means that when resolving an object from its URL, care must
be taken to factor in the language segment of the URL too.

When using this mixin, it is important to also set the
``slug_source_field_name`` property on the implementing model to the name of
the translated field which the slug is to be derived from. If you require more
slugs to be derived from multiple fields (translated or otherwise), simply
override the method ``get_slug_source`` to provide the source string for the
slug.

Configuration properties
************************

slug_default
~~~~~~~~~~~~
Provide a lazy translated string to use for the default slug should an object
not have a source string to derive a slug from.

slug_field_name
~~~~~~~~~~~~~~~
Provide the name of the translated field in which generated slug shall
be stored.

slug_globally_unique
~~~~~~~~~~~~~~~~~~~~
A boolean flag controlling whether slugs are globally unique, or only unique
with each language. Default value is False.

slug_max_length
~~~~~~~~~~~~~~~
Declares the max_length of slugs. This defaults to the ``max_length`` of the
slug_field and is determined via introspection.

slug_separator
~~~~~~~~~~~~~~
This determines the separator used before any index added to the slug. It does
**not** determine the separator used in the slug itself, which is always ``-``.
This is only provided for compatibility with the slugify()`` method in
aldryn_common, but it is not recommended to be used. Defaults to ``-``.

slug_source_field_name
~~~~~~~~~~~~~~~~~~~~~~
Provide the name of the translated field to be used for deriving the slug.
If more than one field, or other complex sources are required, override the
method ``get_slug_source()`` instead. Note that if ``get_slug_source()`` is
overriden, it is recommended to also override ``get_slug_default()``.


Public methods
**************

get_slug_default
~~~~~~~~~~~~~~~~

Naively constructs a translated default slug from the object. For better
results, just set the `slug_default` property on the class to a lazy
translated string. Alternatively, override this method if you need to more
programmtically determine the default slug.

Example: If your model is "news article" and your source field is "title" this
will return "news-article-without-title".


get_slug_max_length
~~~~~~~~~~~~~~~~~~~
Accepts an optional parameter ``idx_len``.

Introspects the slug field to determine the maximum length, taking into account
a possible separator and up to a [idx_len]-digit number.


get_slug_source
~~~~~~~~~~~~~~~
Simply returns the value of the slug source field. Override for more complex
situations such as using multiple fields (translated or not) as the source.


models.TranslationHelperMixin
-----------------------------

Public Methods
**************


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


.. |PyPI Version| image:: https://badge.fury.io/py/aldryn-translation-tools.svg
   :target: https://pypi.python.org/pypi/aldryn-translation-tools
.. |Coverage status| image:: https://travis-ci.org/aldryn/aldryn-translation-tools.svg
   :target: https://travis-ci.org/aldryn/aldryn-translation-tools
