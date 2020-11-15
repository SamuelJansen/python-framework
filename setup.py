from distutils.core import setup
import os, site

VERSION = '0.0.1-102'
NAME = 'python_framework'
URL = f'https://github.com/SamuelJansen/{NAME}/'

OS_SEPARATOR = os.path.sep
BACK_SLASH = '\\'
SLASH = '/'
PYTHON_LANGUAGE_NAME = 'python'
STATIC_DIRECTORY_PATH = f'{OS_SEPARATOR}statics'
SWAGGER_RELATIVE_PATH = f'{NAME}{OS_SEPARATOR}api{OS_SEPARATOR}resource{OS_SEPARATOR}swaggerui'
SETUP_LOG_LABEL = '[SETUP  ] '

def getStaticPackagePath() :
    ###- /app/.heroku/python/statics/python_framework/api/resource/swaggerui/
    staticPackageList = site.getsitepackages()
    print(f'{SETUP_LOG_LABEL}Static package list: {staticPackageList}. Picking the first one')
    staticPackage = str(staticPackageList[0])
    staticPackage = staticPackage.replace(f'{BACK_SLASH}{BACK_SLASH}',OS_SEPARATOR)
    staticPackage = staticPackage.replace(SLASH,OS_SEPARATOR)
    staticPackage = staticPackage.replace(BACK_SLASH,OS_SEPARATOR)
    staticPackage = f'{staticPackage.split(PYTHON_LANGUAGE_NAME)[0]}'
    if not staticPackage[-1] == str(OS_SEPARATOR) :
        staticPackage = f'{staticPackage}{OS_SEPARATOR}'
    staticPackage = f'{staticPackage}{PYTHON_LANGUAGE_NAME}{STATIC_DIRECTORY_PATH}'
    print(f'{SETUP_LOG_LABEL}Static package: "{staticPackage}"')
    return staticPackage

staticPackagePath = f'{getStaticPackagePath()}{OS_SEPARATOR}{SWAGGER_RELATIVE_PATH}'

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
        (staticPackagePath, [
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
        'globals==0.1.0-03'
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8'
    ]
)
