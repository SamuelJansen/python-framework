from distutils.core import setup
import os

version = '0.0.1-76'
name = 'python_framework'
url = f'https://github.com/SamuelJansen/{name}/'

OS_SEPARATOR = os.path.sep

# distPackage = f'lib{OS_SEPARATOR}site-packages'
distPackage = f'dist'

swaggerRelativePath = f'{OS_SEPARATOR}api{OS_SEPARATOR}resource{OS_SEPARATOR}swaggerui'

setup(
    name = name,
    packages = [
        name,
        f'{name}{OS_SEPARATOR}api',
        f'{name}{OS_SEPARATOR}api{OS_SEPARATOR}src',
        f'{name}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}annotation',
        f'{name}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}model',
        f'{name}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}domain',
        f'{name}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}helper',
        f'{name}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service',
        f'{name}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service{OS_SEPARATOR}openapi',
        f'{name}{OS_SEPARATOR}api{OS_SEPARATOR}src{OS_SEPARATOR}service{OS_SEPARATOR}flask',
        f'{name}{OS_SEPARATOR}api{OS_SEPARATOR}resource',
        f'{name}{OS_SEPARATOR}api{OS_SEPARATOR}resource{OS_SEPARATOR}swaggerui'
    ],
    data_files = [
        (f'{distPackage}{OS_SEPARATOR}{name}{swaggerRelativePath}', [
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}favicon-16x16.png',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}favicon-32x32.png',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}index.template.html',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}oauth2-redirect.html',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}swagger-ui-bundle.js',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}swagger-ui-bundle.js.map',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}swagger-ui-standalone-preset.js',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}swagger-ui-standalone-preset.js.map',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}swagger-ui.css',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}swagger-ui.css.map',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}swagger-ui.js',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}swagger-ui.js.map',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}LICENSE',
            f'{name}{swaggerRelativePath}{OS_SEPARATOR}VERSION'
        ])
    ],
    version = version,
    license = 'MIT',
    description = 'Flask wrapper',
    author = 'Samuel Jansen',
    author_email = 'samuel.jansenn@gmail.com',
    url = url,
    download_url = f'{url}archive/v{version}.tar.gz',
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
        'globals==0.0.43-9',
        'python_helper==0.0.14'
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8'
    ]
)
