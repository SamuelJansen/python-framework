from distutils.core import setup
import os

print('''Installation on linux, run:
sudo apt install libpq-dev python3-dev
pip3.9 install --no-cache-dir python-framework --force --upgrade

Aliases:
sudo rm /usr/bin/python
sudo ln -s /usr/local/bin/pythonX.Y /usr/bin/python

sudo rm /usr/bin/pip
sudo ln -s /usr/local/bin/pipX.Y /usr/bin/pip
''')

VERSION = '0.3.97'

NAME = 'python_framework'
PACKAGE_NAME = NAME
REPOSITORY_NAME = NAME.replace("_", "-")
URL = f'https://github.com/SamuelJansen/{REPOSITORY_NAME}/'

OS_SEPARATOR = os.path.sep

setup(
    name = NAME,
    packages = [
        PACKAGE_NAME,
        f'{PACKAGE_NAME}{OS_SEPARATOR}api',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}annotation',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}annotation{OS_SEPARATOR}client',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}model',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}util',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}domain',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}constant',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}controller',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}converter',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}converter{OS_SEPARATOR}static',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}repository',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}enumeration',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}dto',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service{OS_SEPARATOR}openapi',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service{OS_SEPARATOR}flask',
        f'{PACKAGE_NAME}{OS_SEPARATOR}api{OS_SEPARATOR}resource'
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
        'Flask==2.2.2',
        'Flask-RESTful==0.3.9',
        'PyJWT==2.4.0',
        'Flask-Cors==3.0.9',
        'Flask-Swagger-Ui==3.36.0',
        'psycopg2-binary<3.0,>=2.8.6',
        'SQLAlchemy==1.4.25',
        'globals<1.0,>=0.3.34',
        'python-helper<1.0,>=0.3.52',
        'Flask-APScheduler==1.12.2',
        'requests<3.0,>=2.26.0',
        'werkzeug<3.0,>=2.2.2'
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7'
    ],
    python_requires='>=3.7'
)
