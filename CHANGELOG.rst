=========
Changelog
=========

0.3.0 (unreleased)
==================

* Added support for Django 1.11, 2.0 and 2.1
* Removed support for Django < 1.11
* Adapted testing infrastructure (tox/travis) to incorporate
  django CMS 3.5 and 3.6


0.2.1 (2015-11-02)
==================

* Fixed slug uniqueness check in TranslatedAutoSlugifyMixin


0.2.0 (2015-10-22)
==================

* Moved to python-slugify instead of Django slugify for slug generation


0.1.2 (2015-08-18)
==================

* Added I18NSitemap helper class
* Added get_admin_url() and get_object_from_request() utility methods


0.1.1 (2015-08-13)
==================

* Fixed an issue where a None could be returned from get_slug_max_length()
* Fixed an issue relating to language names that include unicode symbols


0.1.0 (2015-07-27)
==================

* Added models.TranslatedAutoSlugMixin

