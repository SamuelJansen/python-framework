from distutils.core import setup

version = '0.0.1-50'
name = 'python_framework'
url = f'https://github.com/SamuelJansen/{name}/'

dataFilePackage = "Lib/site-packages"

swaggerRelativePath = "/api/resource/swaggerui"

setup(
    name = name,
    packages = [
        name,
        f'{name}/api',
        f'{name}/api/src',
        f'{name}/api/src/annotation',
        f'{name}/api/src/model',
        f'{name}/api/src/domain',
        f'{name}/api/src/helper',
        f'{name}/api/src/service',
        f'{name}/api/src/service/openapi',
        f'{name}/api/src/service/flask',
        f'{name}/api/resource',
        f'{name}/api/resource/swaggerui'
    ],
    data_files = [
        (f'{dataFilePackage}/{name}{swaggerRelativePath}', [
            f'{name}{swaggerRelativePath}/favicon-16x16.png',
            f'{name}{swaggerRelativePath}/favicon-32x32.png',
            f'{name}{swaggerRelativePath}/index.template.html',
            f'{name}{swaggerRelativePath}/oauth2-redirect.html',
            f'{name}{swaggerRelativePath}/swagger-ui-bundle.js',
            f'{name}{swaggerRelativePath}/swagger-ui-bundle.js.map',
            f'{name}{swaggerRelativePath}/swagger-ui-standalone-preset.js',
            f'{name}{swaggerRelativePath}/swagger-ui-standalone-preset.js.map',
            f'{name}{swaggerRelativePath}/swagger-ui.css',
            f'{name}{swaggerRelativePath}/swagger-ui.css.map',
            f'{name}{swaggerRelativePath}/swagger-ui.js',
            f'{name}{swaggerRelativePath}/swagger-ui.js.map',
            f'{name}{swaggerRelativePath}/LICENSE',
            f'{name}{swaggerRelativePath}/VERSION'
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
        "gunicorn>=0",
        "Flask>=0",
        "Flask-RESTful>=0",
        "Flask-JWT-Extended>=0",
        "Flask-Swagger-Ui>=0",
        "psycopg2-binary>=0",
        "SQLAlchemy>=0",
        "globals==0.0.42",
        "python_helper==0.0.14"
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8'
    ]
)
