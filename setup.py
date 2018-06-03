from distutils.core import setup
from setuptools import find_packages


setup(
    name='menucli',
    version=0.1,
    install_requires=['requests', 'PyYAML'],
    entry_points={
        'console_scripts': [
            'menucli = menucli.menu_cli:main',
        ]
    },
    url='',
    author='Elod Illes',
    description='Fetch daily offer of Restaurants in CLI',
    packages=find_packages(),
)
