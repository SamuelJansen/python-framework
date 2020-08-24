from distutils.core import setup

version = '0.0.1-3'
name = 'python_framework'
url = f'https://github.com/SamuelJansen/{name}/'

setup(
    name = name,
    packages = [
        name,
        f'{name}/api',
        f'{name}/api/resource',
        f'{name}/api/resource/swaggerui',
        f'{name}/api/src',
        f'{name}/api/src/annotation',
        f'{name}/api/src/helper',
        f'{name}/api/src/service',
        f'{name}/api/src/service/openapi',
        f'{name}/api/src/service/flask'
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

    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8'
    ]
)
