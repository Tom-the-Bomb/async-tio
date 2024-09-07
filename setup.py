from setuptools import setup
import re


version = None
readme = None
requirements = []

with open('README.md') as r:
    readme = r.read()

with open('requirements.txt') as reqs:
    requirements = reqs.read().splitlines()

with open('async_tio/__init__.py') as f:
    version = re.search(r"^__version__\s*=\s*[\'']([^\'']*)[\'']", f.read(), re.MULTILINE).group(1)

setup(
    name='async_tio',
    author='Tom-the-Bomb',
    version=version,
    description='An unoffical API wrapper for tio.run',
    long_description=readme,
    long_description_content_type='text/markdown',
    license= 'MIT',
    url='https://github.com/Tom-the-Bomb/async-tio',
    project_urls={
        'Repository': 'https://github.com/Tom-the-Bomb/async-tio',
        'Issue tracker': 'https://github.com/Tom-the-Bomb/async-tio/issues',
    },
    classifiers =[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    include_package_data=True,
    packages=['async_tio'],
    install_requires=requirements,
    zip_safe=True,
    python_requires='>=3.8'
)