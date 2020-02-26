from setuptools import setup, find_packages

setup(
    name='kovaak_stats_back',
    version='0.0',
    description='',
    author=[
        "Guillaume Roche"
    ],
    author_email=[
        "guillaumerocheg@gmail.com"
    ],
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-restplus',
        'Flask-sqlalchemy',
        'Flask-migrate',
        'Flask-login',
        'Flask-session',
        'bcrypt',
        'jsonpatch',
        'jsonpointer',
        'requests_oauthlib'
    ],
    include_package_data=True,
    data_files=[
        ('www/kovaak_stats_back/app', ['app/app.py']),
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.8",
        "Framework :: Flask",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'kovaak_stats=kovaak_stats.cli:main',
        ],
    },
)
print(find_packages())
