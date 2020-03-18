from setuptools import setup
import sys
import json


with open('metadata.json', encoding='utf-8') as fp:
    metadata = json.load(fp)


setup(
    name='lexibank_wangbai',
    description=metadata['title'],
    license=metadata.get('license', ''),
    url=metadata.get('url', ''),
    py_modules=['lexibank_wangbai'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'lexibank.dataset': [
            'wangbai=lexibank_wangbai:Dataset',
        ],
        'cldfbench.commands': [
            'wangbai=wangbaicommands',
        ],

    },
    install_requires=[
        'pylexibank>=1.1.1',
    ]
)
