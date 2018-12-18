# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

from aldryn_translation_tools import __version__


REQUIREMENTS = [
    'django-cms>=3.4.5',
    'django-parler>=1.9.2',
    'Unidecode>=1.0.23',
    'python-slugify>=1.2.6',
]


setup(
    name='aldryn-translation-tools',
    version=__version__,
    description='Collection of helpers and mixins for translated projects',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/aldryn/aldryn-translation-tools',
    packages=find_packages(exclude=['tests']),
    license='LICENSE.txt',
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    classifiers=[
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
    ],
    include_package_data=True,
    zip_safe=False
)
