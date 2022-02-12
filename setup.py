# -*- coding: utf-8 -*-

import setuptools

setuptools.setup(
    name='eco-counter-fetcher',
    version='1.0.0',
    author='Christoph Böhme',
    author_email='christoph@b3e.net',
    description='',
    url='https://github.com/cboehme/eco-counter-fetcher',
    license='GPL-2',
    packages=setuptools.find_packages(),
    install_requires=[
        "requests==2.27.0"
    ],
    entry_points={
        'console_scripts': [
            'ecf-list-counters=ecocounterfetcher.fetcher:list_counters',
            'ecf-show-info=ecocounterfetcher.fetcher:show_info',
            'ecf-fetch-counter=ecocounterfetcher.fetcher:fetch_counter'
        ],
    }
)
