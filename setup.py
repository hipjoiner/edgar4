from setuptools import setup, find_packages


with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='edgar4',
    version='2020.2.10',
    author='John Pirie',
    author_email='john@thepiries.net',
    description='Pip-installable SEC Edgar tools',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hipjoiner/edgar4',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'requests', 'lxml', 'beautifulsoup4'
    ],
    entry_points={
        'console_scripts': [
        ],
    }
)
