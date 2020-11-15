from distutils.core import setup
import os, site

VERSION = '0.0.1-111'
NAME = 'python_framework'
URL = f'https://github.com/SamuelJansen/{NAME}/'

OS_SEPARATOR = os.path.sep
PYTHON_VERSION = 3.8
SWAGGER_RELATIVE_PATH = f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}resource{OS_SEPARATOR}swaggerui'
STATIC_PACKAGE_PATH = f'statics{OS_SEPARATOR}{SWAGGER_RELATIVE_PATH}'
STATIC_DIRECTORY_PATH = f'{OS_SEPARATOR}lib{OS_SEPARATOR}python{PYTHON_VERSION}{OS_SEPARATOR}site-packages{OS_SEPARATOR}statics'
print(f'[SETUP  ] Static package: "{STATIC_PACKAGE_PATH}"')

setup(
    name = NAME,
    packages = [
        NAME,
        f'{NAME}{OS_SEPARATOR}api',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}annotation',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}model',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}domain',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}helper',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service{OS_SEPARATOR}openapi',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service{OS_SEPARATOR}flask',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}resource',
        f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}resource{OS_SEPARATOR}swaggerui'
    ],
    data_files = [
        (STATIC_PACKAGE_PATH, [
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}favicon-16x16.png',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}favicon-32x32.png',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}index.template.html',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}oauth2-redirect.html',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}swagger-ui-bundle.js',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}swagger-ui-bundle.js.map',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}swagger-ui-standalone-preset.js',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}swagger-ui-standalone-preset.js.map',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}swagger-ui.css',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}swagger-ui.css.map',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}swagger-ui.js',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}swagger-ui.js.map',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}LICENSE',
            f'{SWAGGER_RELATIVE_PATH}{OS_SEPARATOR}VERSION'
        ])
    ],
    version = VERSION,
    license = 'MIT',
    description = 'Flask wrapper',
    author = 'Samuel Jansen',
    author_email = 'samuel.jansenn@gmail.com',
    url = URL,
    download_url = f'{URL}archive/v{VERSION}.tar.gz',
    keywords = ['flask', 'sqlalchemy', 'open api', 'jwt', 'serializer'],
    install_requires = [
        'gunicorn==20.0.4',
        'Flask==1.1.2',
        'Flask-RESTful==0.3.8',
        'Flask-JWT-Extended==3.24.1',
        'flask-restful-swagger-2==0.35',
        'safrs==2.10.4',
        'Flask-Swagger-Ui==3.36.0',
        'psycopg2-binary==2.8.6',
        'SQLAlchemy==1.3.20',
        'globals==0.1.0-11'
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8'
    ]
)
