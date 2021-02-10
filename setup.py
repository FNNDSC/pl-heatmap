from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.rst')) as f:
    readme = f.read()

setup(
    name             = 'heatmap',
    version          = '2.0.0',
    description      = """
        A ChRIS DS plugin that compares two different image sets
        and generates useful difference image data and metrics.
    """,
    long_description = readme,
    author           = 'FNNDSC Developers',
    author_email     = 'dev@babymri.org',
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
