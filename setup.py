# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_translation_tools import __version__

REQUIREMENTS = [
    'django-cms>=3.0.12',
    'django-parler>=1.4',
    'Unidecode>=0.4.18,<=0.5',
    'python-slugify>=1.1.4,<=1.2',
]

CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(
    name='aldryn-translation-tools',
    version=__version__,
    description='Collection of helpers and mixins for translated projects',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/aldryn/aldryn-translation-tools',
    packages=find_packages(),
    license='LICENSE.txt',
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False
)
