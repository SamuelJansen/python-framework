from distutils.core import setup
import os

print('''Installation on linux, run:
sudo apt install libpq-dev python3-dev
pip3.9 install --no-cache-dir python-framework --force --upgrade

Aliases:
sudo rm /usr/bin/python
sudo ln -s /usr/local/bin/python3.9 /usr/bin/python

sudo rm /usr/bin/pip
sudo ln -s /usr/local/bin/pip3.9 /usr/bin/pip
''')

VERSION = '0.2.6'
NAME = 'python_framework'
URL = f'https://github.com/SamuelJansen/{NAME}/'

OS_SEPARATOR = os.path.sep

setup(
    name = NAME,
    packages = [
        NAME,
        f'{NAME}{OS_SEPARATOR}api',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}annotation',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}model',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}helper',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}controller',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}converter',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}converter{OS_SEPARATOR}static',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}repository',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}enumeration',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}dto',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service{OS_SEPARATOR}openapi',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service{OS_SEPARATOR}flask',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}resource'
    ],
    # data_files = [
    #     (STATIC_PACKAGE_PATH, [
    #         f'{RELATIVE_PATH}{OS_SEPARATOR}resource_1.extension',
    #         f'{RELATIVE_PATH}{OS_SEPARATOR}resource_2.extension'
    #     ])
    # ],
    version = VERSION,
    license = 'MIT',
    description = 'Flask wrapper',
    author = 'Samuel Jansen',
    author_email = 'samuel.jansenn@gmail.com',
    url = URL,
    download_url = f'{URL}archive/v{VERSION}.tar.gz',
    keywords = ['flask', 'sqlalchemy', 'open api', 'jwt', 'serializer', 'scheduler'],
    install_requires = [
        'gunicorn==20.0.4',
        'Flask==1.1.4', ###- 1.1.2',
        'Flask-RESTful==0.3.8',
        'Flask-JWT-Extended==3.25.0',
        'Flask-Cors==3.0.9',
        'Flask-Swagger-Ui==3.36.0',
        'psycopg2-binary==2.8.6',
        # 'SQLAlchemy==1.4.25', ###- trashy SqlAlchemy job with that registry keyword...
        'SQLAlchemy==1.3.20',
        'globals>=0.3.4',
        'python_helper>=0.3.8',
        'Flask-APScheduler==1.12.2',
        'psutil==5.8.0',
        'requests==2.26.0'
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9'
    ]
)
