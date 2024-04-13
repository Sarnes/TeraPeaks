from setuptools import setup, find_packages

setup(
    name='TeraPeaks API',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'search = TerPeaksAPI.api:main',
        ],
    },
    install_requires=[
        'certifi==2024.2.2',
        'charset-normalizer==3.3.2',
        'emoji==2.11.0',
        'exceptiongroup==1.2.0',
        'greenlet==3.0.3',
        'idna==3.6',
        'iniconfig==2.0.0',
        'packaging==24.0',
        'playwright==1.43.0',
        'pluggy==1.4.0',
        'pyee==11.1.0',
        'pytest==8.1.1',
        'pytest-base-url==2.1.0',
        'pytest-playwright==0.4.4',
        'python-slugify==8.0.4',
        'requests==2.31.0',
        'requests-toolbelt==1.0.0',
        'soupsieve==2.5',
        'text-unidecode==1.3',
        'tomli==2.0.1',
        'typing_extensions==4.11.0',
        'undetected-playwright==0.2.0',
        'urllib3==2.2.1'
    ],
)