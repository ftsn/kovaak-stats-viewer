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
        'bcrypt'
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
    test_suite='tests'
)
print(find_packages())
