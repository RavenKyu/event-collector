from setuptools import setup, find_packages

__version__ = '1.0.0b'

LONG_DESCRIPTION = open("README.md", "r", encoding="utf-8").read()

tests_require = [
    'pytest',
    'pytest-mock',
]

setup(
    name="event-collector",
    version=__version__,
    author="Duk Kyu Lim",
    author_email="deokyu@vivans.net",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    description='Event Collector',
    url="",
    license="MIT",
    keywords=[],
    install_requires=[
        'apscheduler',
        'click==7.1.2',
        'celery',
        'flask==1.1.1',
        'PyYaml',
        'requests',
        'redis'
    ],
    tests_require=tests_require,
    package_dir={"event_collector": "event_collector"},
    packages=find_packages(
        where='.',
        include=['event_collector',
                 'event_collector.*'],
        exclude=['dummy-*', 'tests', 'tests.*']),
    package_data={
        "": ["*.cfg"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': [
            'event-collector=event_collector.__main__:main',
        ],
    },
    zip_safe=False,
)
