# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    from urllib import urlencode
except ImportError:  # pragma: no cover
    from urllib.parse import urlencode

from django.utils.translation import get_language_from_request

from cms.utils.urlutils import admin_reverse
from parler.models import TranslatableModel


def get_admin_url(action, action_args=[], **url_args):
    """
    Convenience method for constructing admin-urls with GET parameters.

    :param action:      The admin url key for use in reverse. E.g.,
                        'things_edit_thing'
    :param action_args: The url args for the reverse. E.g., [thing.pk, ]
    :param url_args:    A dict of key/value pairs for GET parameters. E.g.,
                        {'language': 'en', }.
    :return: The complete admin url
    """
    base_url = admin_reverse(action, args=action_args)
    # Converts [{key: value}, …] => ["key=value", …]
    # We sort the dict into a sequence of tuples for predictability. Testing
    # reveals that different versions of Python/Django behave differently, which
    # make it complicated to run tests, if nothing else.
    url_args_tuple = sorted([(k, v) for k, v in url_args.items()])
    params = urlencode(url_args_tuple)
    if params:
        return "?".join([base_url, params])
    else:
        return base_url


def get_object_from_request(model, request,
                            pk_url_kwarg='pk',
                            slug_url_kwarg='slug',
                            slug_field='slug'):
    """
    Given a model and the request, try to extract and return an object
    from an available 'pk' or 'slug', or return None.

    Note that no checking is done that the obj's kwargs really are for objects
    matching the provided model (how would it?) so use only where appropriate.
    """
    language = get_language_from_request(request, check_path=True)
    kwargs = request.resolver_match.kwargs
    mgr = model.objects
    if pk_url_kwarg in kwargs:
        return mgr.filter(pk=kwargs[pk_url_kwarg]).first()
    elif slug_url_kwarg in kwargs:
        # If the model is translatable, and the given slug is a translated
        # field, then find it the Parler way.
        filter_kwargs = {slug_field: kwargs[slug_url_kwarg]}
        try:
            translated_fields = model._parler_meta.get_translated_fields()
        except AttributeError:
            translated_fields = []
        if (issubclass(model, TranslatableModel) and
                slug_url_kwarg in translated_fields):
            return mgr.active_translations(language, **filter_kwargs).first()
        else:
            # OK, do it the normal way.
            return mgr.filter(**filter_kwargs).first()
    else:
        return None
