from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.rst')) as f:
    readme = f.read()

setup(
    name             = 'heatmap',
    version          = '0.1',
    description      = 'An app to compare a set of 2 different png (256x256 px) images and generate a heatmap',
    long_description = readme,
    author           = 'Sandip Samal',
    author_email     = 'sandip.samal@childrens.harvard.edu',
    url              = 'http://wiki',
    packages         = ['heatmap'],
    install_requires = ['chrisapp'],
    test_suite       = 'nose.collector',
    tests_require    = ['nose'],
    license          = 'MIT',
    zip_safe         = False,
    python_requires  = '>=3.8',
    entry_points     = {
        'console_scripts': [
            'heatmap = heatmap.__main__:main'
            ]
        }
)
